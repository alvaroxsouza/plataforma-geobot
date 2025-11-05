"""
Modelo de análise de IA
"""
from sqlalchemy import (
    BigInteger, Column, DateTime, Enum, ForeignKey, Numeric, Text, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base
from .enums import TipoAnalise


class Analise(Base):
    """Modelo de análise de IA"""
    __tablename__ = "analises"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    fiscalizacao_id = Column(BigInteger, ForeignKey("fiscalizacoes.id", ondelete="CASCADE"), nullable=False)
    tipo_analise = Column(Enum(TipoAnalise, name="tipo_analise", values_callable=lambda x: [e.value for e in x]), nullable=False)
    dados_json = Column(JSONB, default=dict, nullable=False)
    resultado_principal = Column(Text)
    confianca = Column(Numeric(5, 2))
    processado_em = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    fiscalizacao = relationship("Fiscalizacao", back_populates="analises")
    arquivos = relationship("ArquivoAnalise", back_populates="analise")

    __table_args__ = (
        CheckConstraint("confianca IS NULL OR (confianca >= 0 AND confianca <= 100)", name="confianca_valida"),
    )

