"""
Modelo de fiscalização
"""
from sqlalchemy import (
    BigInteger, Column, DateTime, Enum, ForeignKey, String, Text, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base
from .enums import StatusFiscalizacao


class Fiscalizacao(Base):
    """Modelo de fiscalização"""
    __tablename__ = "fiscalizacoes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    denuncia_id = Column(BigInteger, ForeignKey("geobot.denuncias.id", ondelete="RESTRICT"), nullable=False)
    fiscal_id = Column(BigInteger, ForeignKey("geobot.usuarios.id", ondelete="RESTRICT"), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(StatusFiscalizacao, name="status_fiscalizacao", values_callable=lambda x: [e.value for e in x]), default=StatusFiscalizacao.AGUARDANDO, nullable=False)
    data_inicializacao = Column(DateTime(timezone=True))
    data_conclusao = Column(DateTime(timezone=True))
    observacoes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    denuncia = relationship("Denuncia", back_populates="fiscalizacoes")
    fiscal = relationship("Usuario", back_populates="fiscalizacoes", foreign_keys="Fiscalizacao.fiscal_id")
    analises = relationship("Analise", back_populates="fiscalizacao")
    etapas = relationship("EtapaFiscalizacao", back_populates="fiscalizacao", cascade="all, delete-orphan")
    arquivos_fiscalizacao = relationship("ArquivoFiscalizacao", back_populates="fiscalizacao", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("data_conclusao IS NULL OR data_conclusao >= data_inicializacao", name="datas_validas"),
        {'schema': 'geobot'}
    )

