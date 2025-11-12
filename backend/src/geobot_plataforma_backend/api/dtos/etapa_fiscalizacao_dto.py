"""
DTOs para operações de etapas e análise de fiscalizações
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EtapaFiscalizacaoStatus(str, Enum):
    """Status das etapas de fiscalização"""
    PENDENTE = "pendente"
    SOBREVOO = "sobrevoo"
    ABASTECIMENTO = "abastecimento"
    ANALISE_IA = "analise_ia"
    RELATORIO = "relatorio"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class DeteccaoDTO(BaseModel):
    """DTO para uma detecção encontrada pela IA"""
    tipo: str  # Ex: "erosão", "desmatamento", "construção irregular"
    confianca: float  # 0-1 ou 0-100
    localizacao: Optional[Dict[str, Any]] = None  # Coordenadas ou bbox
    descricao: Optional[str] = None
    severidade: Optional[str] = None  # "baixa", "média", "alta", "crítica"

    class Config:
        from_attributes = True


class ResultadoAnaliseIADTO(BaseModel):
    """DTO para resultado da análise de IA"""
    id: int
    uuid: str
    etapa_id: int
    job_id: Optional[str] = None
    deteccoes: List[DeteccaoDTO]
    confianca_media: float
    classificacao_geral: Optional[str] = None
    modelo_utilizado: Optional[str] = None
    versao_modelo: Optional[str] = None
    tempo_processamento_segundos: Optional[float] = None
    status_processamento: str
    created_at: datetime

    class Config:
        from_attributes = True


class ArquivoFiscalizacaoDTO(BaseModel):
    """DTO para arquivo de fiscalização"""
    id: int
    uuid: str
    fiscalizacao_id: int
    etapa_id: Optional[int] = None
    tipo: str  # foto_sobrevoo, resultado_ia, etc
    nome_original: str
    url_blob: str
    tamanho_bytes: int
    mime_type: str
    metadados: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EtapaFiscalizacaoDTO(BaseModel):
    """DTO para etapa de fiscalização"""
    id: int
    uuid: str
    fiscalizacao_id: int
    etapa: EtapaFiscalizacaoStatus
    iniciada_em: datetime
    concluida_em: Optional[datetime] = None
    progresso_percentual: float
    dados: Optional[Dict[str, Any]] = None
    resultado: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RelatórioFiscalizacaoDTO(BaseModel):
    """DTO para relatório de fiscalização"""
    id: int
    uuid: str
    fiscalizacao_id: int
    etapa_id: int
    titulo: str
    resumo_executivo: Optional[str] = None
    conclusoes: Optional[str] = None
    recomendacoes: Optional[str] = None
    dados_relatorio: Dict[str, Any]
    url_documento: Optional[str] = None
    status: str  # rascunho, final, assinado
    gerado_em: datetime
    assinado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class IniciarFiscalizacaoDTO(BaseModel):
    """DTO para iniciar uma fiscalização"""
    fiscalizacao_id: int
    dados_iniciais: Optional[Dict[str, Any]] = None


class UploadArquivoDTO(BaseModel):
    """DTO para upload de arquivo"""
    etapa_id: int
    tipo: str  # foto_sobrevoo
    nome_arquivo: str
    metadados: Optional[Dict[str, Any]] = None


class IniciarAnalisiaIADTO(BaseModel):
    """DTO para iniciar análise de IA"""
    etapa_id: int
    imagens_ids: List[int]  # IDs dos arquivos para processar
    parametros_modelo: Optional[Dict[str, Any]] = None


class GerarRelatórioDTO(BaseModel):
    """DTO para gerar relatório"""
    etapa_id: int
    titulo: str
    resumo_executivo: Optional[str] = None
    conclusoes: Optional[str] = None
    recomendacoes: Optional[str] = None
    resultado_analise_ia_id: Optional[int] = None


class ProgressoFiscalizacaoDTO(BaseModel):
    """DTO com progresso completo da fiscalização"""
    fiscalizacao_id: int
    etapa_atual: EtapaFiscalizacaoStatus
    etapas_concluidas: List[EtapaFiscalizacaoDTO]
    etapa_em_progresso: Optional[EtapaFiscalizacaoDTO] = None
    etapas_pendentes: List[EtapaFiscalizacaoStatus]
    progresso_geral_percentual: float
    arquivos_carregados: int
    resultado_ia: Optional[ResultadoAnaliseIADTO] = None
    relatorio: Optional[RelatórioFiscalizacaoDTO] = None

    class Config:
        from_attributes = True


class TransicaoEtapaDTO(BaseModel):
    """DTO para transicionar entre etapas"""
    fiscalizacao_id: int
    etapa_nova: EtapaFiscalizacaoStatus
    dados: Optional[Dict[str, Any]] = None
