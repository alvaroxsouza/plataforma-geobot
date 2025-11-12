"""
Modelo para rastrear o progresso das etapas de fiscalização
"""
import uuid
from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Float, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.geobot_plataforma_backend.core.database import Base
from src.geobot_plataforma_backend.domain.entity.etapa_fiscalizacao_enum import EtapaFiscalizacaoEnum


class EtapaFiscalizacao(Base):
    """Modelo para rastrear etapas de uma fiscalização"""
    __tablename__ = "etapas_fiscalizacao"
    __table_args__ = {'schema': 'geobot'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Relacionamento com fiscalização
    fiscalizacao_id = Column(BigInteger, ForeignKey("geobot.fiscalizacoes.id", ondelete="CASCADE"), nullable=False)
    fiscalizacao = relationship("Fiscalizacao", back_populates="etapas")
    
    # Enum da etapa
    etapa = Column(SQLEnum(EtapaFiscalizacaoEnum), nullable=False, index=True)
    
    # Timestamps
    iniciada_em = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    concluida_em = Column(DateTime(timezone=True))
    
    # Progresso
    progresso_percentual = Column(Float, default=0.0, nullable=False)  # 0-100
    
    # Dados da etapa (específicos de cada tipo)
    dados = Column(JSONB, nullable=True)  # Armazena dados específicos da etapa
    
    # Resultado/Output
    resultado = Column(JSONB, nullable=True)  # Resultado da etapa
    
    # Status de erro
    erro = Column(Text, nullable=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<EtapaFiscalizacao {self.etapa.value} ({self.progresso_percentual}%)>"


class ArquivoFiscalizacao(Base):
    """Modelo para armazenar referências a arquivos da fiscalização"""
    __tablename__ = "arquivos_fiscalizacao"
    __table_args__ = {'schema': 'geobot'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Relacionamento com fiscalização
    fiscalizacao_id = Column(BigInteger, ForeignKey("geobot.fiscalizacoes.id", ondelete="CASCADE"), nullable=False)
    fiscalizacao = relationship("Fiscalizacao", back_populates="arquivos_fiscalizacao")
    
    # Relacionamento com etapa (opcional)
    etapa_id = Column(Integer, ForeignKey("geobot.etapas_fiscalizacao.id", ondelete="CASCADE"), nullable=True)
    
    # Tipo do arquivo (foto_sobrevoo, resultado_ia, etc)
    tipo = Column(String(50), nullable=False, index=True)
    
    # Informações do arquivo
    nome_original = Column(String(255), nullable=False)
    url_blob = Column(String(500), nullable=False)  # URL no Azure Blob Storage
    tamanho_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Metadados específicos
    metadados = Column(JSONB, nullable=True)  # Ex: coordenadas GPS, altura do drone, etc
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ArquivoFiscalizacao {self.tipo}: {self.nome_original}>"


class ResultadoAnaliseIA(Base):
    """Modelo para armazenar resultados da análise de IA"""
    __tablename__ = "resultados_analise_ia"
    __table_args__ = {'schema': 'geobot'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Relacionamento com etapa
    etapa_id = Column(Integer, ForeignKey("geobot.etapas_fiscalizacao.id", ondelete="CASCADE"), nullable=False)
    etapa = relationship("EtapaFiscalizacao")
    
    # Job do Skypilot
    job_id = Column(String(100), nullable=True)  # ID do job no Skypilot
    
    # Resultados da IA
    deteccoes = Column(JSONB, nullable=False)  # Array com detecções
    confianca_media = Column(Float, nullable=False)  # Confiança média das detecções
    
    # Classificações
    classificacao_geral = Column(String(50), nullable=True)  # ex: "crítico", "moderado", "leve"
    
    # Metadados
    modelo_utilizado = Column(String(100), nullable=True)  # Nome do modelo de IA
    versao_modelo = Column(String(50), nullable=True)
    tempo_processamento_segundos = Column(Float, nullable=True)
    
    # Status do processamento
    status_processamento = Column(String(50), default="pendente", nullable=False)  # pendente, processando, concluído, erro
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ResultadoAnaliseIA confiança={self.confianca_media}%>"


class RelatórioFiscalizacao(Base):
    """Modelo para armazenar relatórios gerados"""
    __tablename__ = "relatorios_fiscalizacao"
    __table_args__ = {'schema': 'geobot'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Relacionamento com fiscalização
    fiscalizacao_id = Column(BigInteger, ForeignKey("geobot.fiscalizacoes.id", ondelete="CASCADE"), nullable=False)
    
    # Relacionamento com etapa
    etapa_id = Column(Integer, ForeignKey("geobot.etapas_fiscalizacao.id", ondelete="CASCADE"), nullable=False)
    
    # Conteúdo do relatório
    titulo = Column(String(255), nullable=False)
    resumo_executivo = Column(Text, nullable=True)
    conclusoes = Column(Text, nullable=True)
    recomendacoes = Column(Text, nullable=True)
    
    # Dados estruturados
    dados_relatorio = Column(JSONB, nullable=False)  # Contém todos os dados do relatório
    
    # Arquivo do relatório (PDF, etc)
    url_documento = Column(String(500), nullable=True)  # URL para download do relatório
    
    # Status
    status = Column(String(50), default="rascunho", nullable=False)  # rascunho, final, assinado
    
    # Timestamps
    gerado_em = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    assinado_em = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<RelatórioFiscalizacao {self.titulo}>"
