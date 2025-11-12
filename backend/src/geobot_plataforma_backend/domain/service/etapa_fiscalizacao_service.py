"""
Serviço para gerenciar etapas de fiscalização
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.domain.entity.etapa_fiscalizacao_enum import EtapaFiscalizacaoEnum
from src.geobot_plataforma_backend.domain.entity.etapa_e_resultado import (
    EtapaFiscalizacao, ArquivoFiscalizacao, ResultadoAnaliseIA, RelatórioFiscalizacao
)
from src.geobot_plataforma_backend.domain.entity.fiscalizacao import Fiscalizacao
from src.geobot_plataforma_backend.api.dtos.etapa_fiscalizacao_dto import (
    EtapaFiscalizacaoDTO, TransicaoEtapaDTO, ProgressoFiscalizacaoDTO,
    IniciarAnalisiaIADTO, GerarRelatórioDTO, ArquivoFiscalizacaoDTO
)


class EtapaFiscalizacaoService:
    """Serviço para gerenciar etapas de fiscalização"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def iniciar_fiscalizacao(self, fiscalizacao_id: int, dados_iniciais: Optional[Dict[str, Any]] = None) -> EtapaFiscalizacao:
        """Inicia uma fiscalização criando a primeira etapa"""
        # Verificar se fiscalização existe
        fiscalizacao = self.db.query(Fiscalizacao).filter(
            Fiscalizacao.id == fiscalizacao_id,
            Fiscalizacao.deleted_at.is_(None)
        ).first()
        
        if not fiscalizacao:
            raise ValueError(f"Fiscalização {fiscalizacao_id} não encontrada")
        
        # Criar primeira etapa (SOBREVOO)
        etapa = EtapaFiscalizacao(
            fiscalizacao_id=fiscalizacao_id,
            etapa=EtapaFiscalizacaoEnum.SOBREVOO,
            dados=dados_iniciais or {},
            progresso_percentual=0.0
        )
        
        self.db.add(etapa)
        self.db.commit()
        self.db.refresh(etapa)
        
        return etapa
    
    def transicionar_etapa(self, fiscalizacao_id: int, etapa_nova: EtapaFiscalizacaoEnum, dados: Optional[Dict[str, Any]] = None) -> EtapaFiscalizacao:
        """Transiciona de uma etapa para outra"""
        # Verificar se fiscalização existe
        fiscalizacao = self.db.query(Fiscalizacao).filter(
            Fiscalizacao.id == fiscalizacao_id,
            Fiscalizacao.deleted_at.is_(None)
        ).first()
        
        if not fiscalizacao:
            raise ValueError(f"Fiscalização {fiscalizacao_id} não encontrada")
        
        # Buscar etapa atual
        etapa_atual = self.db.query(EtapaFiscalizacao).filter(
            EtapaFiscalizacao.fiscalizacao_id == fiscalizacao_id
        ).order_by(EtapaFiscalizacao.created_at.desc()).first()
        
        if not etapa_atual:
            raise ValueError(f"Nenhuma etapa encontrada para fiscalização {fiscalizacao_id}")
        
        # Validar transição
        if not EtapaFiscalizacaoEnum.pode_transicionar(etapa_atual.etapa, etapa_nova):
            raise ValueError(
                f"Transição inválida: {etapa_atual.etapa.value} -> {etapa_nova.value}"
            )
        
        # Marcar etapa atual como concluída
        etapa_atual.concluida_em = datetime.now(timezone.utc)
        etapa_atual.progresso_percentual = 100.0
        
        # Criar nova etapa
        nova_etapa = EtapaFiscalizacao(
            fiscalizacao_id=fiscalizacao_id,
            etapa=etapa_nova,
            dados=dados or {},
            progresso_percentual=0.0
        )
        
        self.db.add(nova_etapa)
        self.db.commit()
        self.db.refresh(nova_etapa)
        
        return nova_etapa
    
    def atualizar_progresso(self, etapa_id: int, progresso_percentual: float, resultado: Optional[Dict[str, Any]] = None) -> EtapaFiscalizacao:
        """Atualiza o progresso de uma etapa"""
        etapa = self.db.query(EtapaFiscalizacao).filter(
            EtapaFiscalizacao.id == etapa_id
        ).first()
        
        if not etapa:
            raise ValueError(f"Etapa {etapa_id} não encontrada")
        
        etapa.progresso_percentual = min(progresso_percentual, 100.0)
        if resultado:
            etapa.resultado = resultado
        
        self.db.commit()
        self.db.refresh(etapa)
        
        return etapa
    
    def registrar_erro(self, etapa_id: int, erro: str) -> EtapaFiscalizacao:
        """Registra um erro em uma etapa"""
        etapa = self.db.query(EtapaFiscalizacao).filter(
            EtapaFiscalizacao.id == etapa_id
        ).first()
        
        if not etapa:
            raise ValueError(f"Etapa {etapa_id} não encontrada")
        
        etapa.erro = erro
        self.db.commit()
        self.db.refresh(etapa)
        
        return etapa
    
    def obter_progresso_completo(self, fiscalizacao_id: int) -> Dict[str, Any]:
        """Obtém o progresso completo de uma fiscalização"""
        fiscalizacao = self.db.query(Fiscalizacao).filter(
            Fiscalizacao.id == fiscalizacao_id,
            Fiscalizacao.deleted_at.is_(None)
        ).first()
        
        if not fiscalizacao:
            raise ValueError(f"Fiscalização {fiscalizacao_id} não encontrada")
        
        # Buscar todas as etapas
        etapas = self.db.query(EtapaFiscalizacao).filter(
            EtapaFiscalizacao.fiscalizacao_id == fiscalizacao_id
        ).order_by(EtapaFiscalizacao.created_at).all()
        
        if not etapas:
            return {
                "fiscalizacao_id": fiscalizacao_id,
                "etapa_atual": None,
                "etapas_concluidas": [],
                "etapa_em_progresso": None,
                "etapas_pendentes": list(EtapaFiscalizacaoEnum),
                "progresso_geral_percentual": 0.0
            }
        
        # Etapa em progresso é a última sem conclusão
        etapa_em_progresso = None
        etapas_concluidas = []
        
        for etapa in etapas:
            if etapa.concluida_em:
                etapas_concluidas.append(etapa)
            else:
                etapa_em_progresso = etapa
        
        # Calcular progresso geral
        if etapas_concluidas:
            progresso_geral = (len(etapas_concluidas) / 6) * 100  # 6 etapas principais
        else:
            progresso_geral = 0.0
        
        if etapa_em_progresso:
            progresso_geral += (etapa_em_progresso.progresso_percentual / 6)
        
        # Etapas pendentes
        etapas_realizadas = {e.etapa for e in etapas_concluidas}
        etapas_pendentes = [e for e in EtapaFiscalizacaoEnum if e not in etapas_realizadas]
        
        # Contar arquivos
        arquivos = self.db.query(ArquivoFiscalizacao).filter(
            ArquivoFiscalizacao.fiscalizacao_id == fiscalizacao_id
        ).count()
        
        return {
            "fiscalizacao_id": fiscalizacao_id,
            "etapa_atual": etapa_em_progresso.etapa.value if etapa_em_progresso else None,
            "etapas_concluidas": [e.etapa.value for e in etapas_concluidas],
            "etapa_em_progresso": etapa_em_progresso.etapa.value if etapa_em_progresso else None,
            "etapas_pendentes": [e.value for e in etapas_pendentes],
            "progresso_geral_percentual": min(progresso_geral, 100.0),
            "arquivos_carregados": arquivos
        }
    
    def registrar_arquivo(
        self, 
        fiscalizacao_id: int,
        etapa_id: int,
        tipo: str,
        nome_original: str,
        url_blob: str,
        tamanho_bytes: int,
        mime_type: str,
        metadados: Optional[Dict[str, Any]] = None
    ) -> ArquivoFiscalizacao:
        """Registra um arquivo da fiscalização"""
        arquivo = ArquivoFiscalizacao(
            fiscalizacao_id=fiscalizacao_id,
            etapa_id=etapa_id,
            tipo=tipo,
            nome_original=nome_original,
            url_blob=url_blob,
            tamanho_bytes=tamanho_bytes,
            mime_type=mime_type,
            metadados=metadados or {}
        )
        
        self.db.add(arquivo)
        self.db.commit()
        self.db.refresh(arquivo)
        
        return arquivo
    
    def obter_arquivos(self, fiscalizacao_id: int, tipo: Optional[str] = None) -> List[ArquivoFiscalizacao]:
        """Obtém arquivos de uma fiscalização"""
        query = self.db.query(ArquivoFiscalizacao).filter(
            ArquivoFiscalizacao.fiscalizacao_id == fiscalizacao_id
        )
        
        if tipo:
            query = query.filter(ArquivoFiscalizacao.tipo == tipo)
        
        return query.order_by(ArquivoFiscalizacao.created_at.desc()).all()
    
    def registrar_resultado_ia(
        self,
        etapa_id: int,
        deteccoes: List[Dict[str, Any]],
        confianca_media: float,
        job_id: Optional[str] = None,
        modelo_utilizado: Optional[str] = None,
        tempo_processamento: Optional[float] = None
    ) -> ResultadoAnaliseIA:
        """Registra resultado da análise de IA"""
        # Determinar classificação geral baseado em confiança
        if confianca_media >= 0.8:
            classificacao = "crítico"
        elif confianca_media >= 0.6:
            classificacao = "moderado"
        else:
            classificacao = "leve"
        
        resultado = ResultadoAnaliseIA(
            etapa_id=etapa_id,
            job_id=job_id,
            deteccoes=deteccoes,
            confianca_media=confianca_media,
            classificacao_geral=classificacao,
            modelo_utilizado=modelo_utilizado or "modelo_padrao",
            status_processamento="concluído",
            tempo_processamento_segundos=tempo_processamento
        )
        
        self.db.add(resultado)
        self.db.commit()
        self.db.refresh(resultado)
        
        return resultado
    
    def obter_resultado_ia(self, etapa_id: int) -> Optional[ResultadoAnaliseIA]:
        """Obtém resultado de IA de uma etapa"""
        return self.db.query(ResultadoAnaliseIA).filter(
            ResultadoAnaliseIA.etapa_id == etapa_id
        ).first()
    
    def criar_relatorio(
        self,
        fiscalizacao_id: int,
        etapa_id: int,
        titulo: str,
        dados_relatorio: Dict[str, Any],
        resumo_executivo: Optional[str] = None,
        conclusoes: Optional[str] = None,
        recomendacoes: Optional[str] = None,
        url_documento: Optional[str] = None
    ) -> RelatórioFiscalizacao:
        """Cria um relatório de fiscalização"""
        relatorio = RelatórioFiscalizacao(
            fiscalizacao_id=fiscalizacao_id,
            etapa_id=etapa_id,
            titulo=titulo,
            resumo_executivo=resumo_executivo,
            conclusoes=conclusoes,
            recomendacoes=recomendacoes,
            dados_relatorio=dados_relatorio,
            url_documento=url_documento,
            status="rascunho"
        )
        
        self.db.add(relatorio)
        self.db.commit()
        self.db.refresh(relatorio)
        
        return relatorio
    
    def obter_relatorio(self, fiscalizacao_id: int) -> Optional[RelatórioFiscalizacao]:
        """Obtém relatório de uma fiscalização"""
        return self.db.query(RelatórioFiscalizacao).filter(
            RelatórioFiscalizacao.fiscalizacao_id == fiscalizacao_id
        ).order_by(RelatórioFiscalizacao.created_at.desc()).first()
