"""
Serviço para gerenciar uploads em Azure Blob Storage
"""
import os
from typing import Optional, Tuple
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class AzureBlobStorageService:
    """Serviço para gerenciar arquivos no Azure Blob Storage"""
    
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER", "fiscalizacoes")
        self.account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        
        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING não configurado")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
    
    def criar_container_se_nao_existir(self):
        """Cria o container se não existir"""
        try:
            self.blob_service_client.create_container(name=self.container_name)
            print(f"Container '{self.container_name}' criado")
        except Exception as e:
            print(f"Container já existe ou erro: {e}")
    
    def upload_arquivo(
        self,
        arquivo_bytes: bytes,
        nome_arquivo: str,
        etapa: str,
        fiscalizacao_id: int,
        metadados: Optional[dict] = None
    ) -> Tuple[str, str]:
        """
        Faz upload de arquivo para Azure Blob Storage
        
        Returns:
            Tuple[url_blob, nome_blob]
        """
        # Estruturar o caminho no blob storage
        # fiscalizacoes/{fiscalizacao_id}/{etapa}/{timestamp}_{nome_arquivo}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_blob = f"fiscalizacoes/{fiscalizacao_id}/{etapa}/{timestamp}_{nome_arquivo}"
        
        try:
            # Obter cliente do blob específico
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=nome_blob
            )
            
            # Preparar metadata
            metadata = metadados or {}
            metadata["uploaded_at"] = datetime.now().isoformat()
            metadata["etapa"] = etapa
            metadata["fiscalizacao_id"] = str(fiscalizacao_id)
            
            # Upload
            blob_client.upload_blob(arquivo_bytes, overwrite=True, metadata=metadata)
            
            # Gerar URL para acesso
            url_blob = blob_client.url
            
            return url_blob, nome_blob
        except Exception as e:
            raise Exception(f"Erro ao fazer upload: {str(e)}")
    
    def gerar_url_assinada(
        self,
        nome_blob: str,
        expiracao_minutos: int = 60
    ) -> str:
        """
        Gera URL assinada para acesso ao arquivo
        """
        if not self.account_name or not self.account_key:
            raise ValueError("Account name ou key não configurados")
        
        try:
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=nome_blob,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(minutes=expiracao_minutos)
            )
            
            url_assinada = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{nome_blob}?{sas_token}"
            return url_assinada
        except Exception as e:
            raise Exception(f"Erro ao gerar URL assinada: {str(e)}")
    
    def listar_arquivos(
        self,
        caminho: str
    ) -> list:
        """
        Lista arquivos em um caminho específico
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                container=self.container_name
            )
            
            blobs = container_client.list_blobs(name_starts_with=caminho)
            arquivos = []
            
            for blob in blobs:
                arquivos.append({
                    "nome": blob.name,
                    "tamanho": blob.size,
                    "criado": blob.creation_time,
                    "modificado": blob.last_modified,
                    "metadados": blob.metadata
                })
            
            return arquivos
        except Exception as e:
            raise Exception(f"Erro ao listar arquivos: {str(e)}")
    
    def deletar_arquivo(self, nome_blob: str) -> bool:
        """Deleta um arquivo"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=nome_blob
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            raise Exception(f"Erro ao deletar arquivo: {str(e)}")
    
    def obter_informacoes_arquivo(self, nome_blob: str) -> dict:
        """Obtém informações sobre um arquivo"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=nome_blob
            )
            
            properties = blob_client.get_blob_properties()
            
            return {
                "nome": properties.name,
                "tamanho": properties.size,
                "tipo_conteudo": properties.content_settings.content_type,
                "criado": properties.creation_time,
                "modificado": properties.last_modified,
                "metadados": properties.metadata
            }
        except Exception as e:
            raise Exception(f"Erro ao obter informações: {str(e)}")
