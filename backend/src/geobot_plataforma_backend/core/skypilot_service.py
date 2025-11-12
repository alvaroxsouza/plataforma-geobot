"""
Serviço para integração com Skypilot para análise de IA
"""
import os
import subprocess
import json
import yaml
from typing import Optional, Dict, List, Any
from datetime import datetime
import tempfile


class SkypilotIAService:
    """Serviço para provisionar máquinas no Azure via Skypilot e executar análise de IA"""
    
    def __init__(self):
        self.cloud_provider = "azure"
        self.gpu_type = "K80"  # Pode ser ajustado conforme necessário
        self.region = os.getenv("AZURE_REGION", "eastus")
        self.job_queue = []
    
    def criar_config_skypilot(
        self,
        imagens_urls: List[str],
        modelo: str = "yolov8",
        parametros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cria configuração YAML para Skypilot
        
        Args:
            imagens_urls: Lista de URLs das imagens para processar
            modelo: Modelo de IA a usar
            parametros: Parâmetros adicionais para o modelo
        
        Returns:
            Configuração Skypilot
        """
        config = {
            "name": f"analise-ia-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "workdir": ".",
            "setup": self._gerar_setup(),
            "run": self._gerar_comando_run(imagens_urls, modelo, parametros),
            "resources": {
                "cloud": self.cloud_provider,
                "region": self.region,
                "accelerators": f"{self.gpu_type}:1",
                "memory": "8+",
                "disk_size": "50+",
                "use_spot": True,  # Usar spot instances para economizar
            },
            "outputs": {
                "result": "/tmp/result.json"
            }
        }
        
        return config
    
    def _gerar_setup(self) -> str:
        """Gera script de setup para instalar dependências"""
        setup_script = """
set -e
echo "Instalando dependências..."
pip install ultralytics opencv-python numpy pandas requests
echo "Dependências instaladas"
        """
        return setup_script
    
    def _gerar_comando_run(
        self,
        imagens_urls: List[str],
        modelo: str,
        parametros: Optional[Dict[str, Any]] = None
    ) -> str:
        """Gera comando para executar análise"""
        params = parametros or {}
        confianca = params.get("confianca_minima", 0.5)
        
        comando = f"""
python3 << 'EOF'
import json
import sys
from ultralytics import YOLO
import urllib.request
import os

# URLs das imagens
imagens_urls = {json.dumps(imagens_urls)}

# Baixar imagens
imagens_locais = []
for i, url in enumerate(imagens_urls):
    caminho = f"/tmp/imagem_{i}.jpg"
    urllib.request.urlretrieve(url, caminho)
    imagens_locais.append(caminho)

# Carregar modelo
modelo = YOLO("yolov8n.pt")  # nano para rapidez

# Processar imagens
deteccoes = []
for caminho in imagens_locais:
    resultados = modelo(caminho, conf={confianca})
    
    for resultado in resultados:
        for box in resultado.boxes:
            deteccoes.append({{
                "confianca": float(box.conf[0]),
                "classe": int(box.cls[0]),
                "classe_nome": resultado.names[int(box.cls[0])],
                "bbox": box.xyxy[0].tolist()
            }})

# Calcular confiança média
confianca_media = sum([d["confianca"] for d in deteccoes]) / len(deteccoes) if deteccoes else 0

# Salvar resultado
resultado = {{
    "deteccoes": deteccoes,
    "confianca_media": confianca_media,
    "total_deteccoes": len(deteccoes),
    "modelo": "YOLOv8",
    "timestamp": "{datetime.now().isoformat()}"
}}

with open("/tmp/result.json", "w") as f:
    json.dump(resultado, f, indent=2)

print(json.dumps(resultado))
EOF
        """
        return comando
    
    def submeter_job_ia(
        self,
        nome_job: str,
        imagens_urls: List[str],
        modelo: str = "yolov8",
        parametros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submete um job de análise de IA ao Skypilot
        
        Args:
            nome_job: Nome do job
            imagens_urls: URLs das imagens para processar
            modelo: Modelo a usar
            parametros: Parâmetros do modelo
        
        Returns:
            Informações do job submetido
        """
        try:
            # Criar configuração
            config = self.criar_config_skypilot(imagens_urls, modelo, parametros)
            
            # Salvar config em arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config, f)
                config_file = f.name
            
            # Submeter job via Skypilot CLI
            # Este é um exemplo - a implementação real dependeria de como Skypilot é usado
            cmd = ["sky", "launch", "-c", nome_job, config_file]
            
            # Para demonstração, simulamos o resultado
            job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                "job_id": job_id,
                "status": "submitted",
                "nome_job": nome_job,
                "config": config_file,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Erro ao submeter job: {str(e)}")
    
    def obter_status_job(self, job_id: str) -> Dict[str, Any]:
        """Obtém status de um job"""
        try:
            # Implementar verificação real com Skypilot
            return {
                "job_id": job_id,
                "status": "completed",  # ou "running", "failed"
                "progresso": 100,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Erro ao obter status: {str(e)}")
    
    def obter_resultado_job(self, job_id: str) -> Dict[str, Any]:
        """Obtém resultado de um job concluído"""
        try:
            # Buscar arquivo de resultado no Azure Blob Storage ou localmente
            return {
                "deteccoes": [],
                "confianca_media": 0.0,
                "total_deteccoes": 0,
                "modelo": "YOLOv8"
            }
        except Exception as e:
            raise Exception(f"Erro ao obter resultado: {str(e)}")
    
    def cancelar_job(self, job_id: str) -> bool:
        """Cancela um job em execução"""
        try:
            cmd = ["sky", "cancel", job_id]
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            raise Exception(f"Erro ao cancelar job: {str(e)}")


# Serviço singleton
_skypilot_service = None

def obter_skypilot_service() -> SkypilotIAService:
    """Factory para obter instância do serviço"""
    global _skypilot_service
    if _skypilot_service is None:
        _skypilot_service = SkypilotIAService()
    return _skypilot_service
