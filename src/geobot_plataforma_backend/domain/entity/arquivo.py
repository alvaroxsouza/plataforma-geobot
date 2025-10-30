"""
Modelo de arquivo
"""
from sqlalchemy import (
    BigInteger, Column, DateTime, String, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base


class Arquivo(Base):
    """Modelo de arquivo"""
    __tablename__ = "arquivos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    tamanho_bytes = Column(BigInteger, nullable=False)
    tipo_mime = Column(String(100), nullable=False)
    extensao = Column(String(10), nullable=False)
    chave_storage = Column(String(500), unique=True, nullable=False)
    hash_checksum = Column(String(64), nullable=False)
    data_upload = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    denuncias = relationship("ArquivoDenuncia", back_populates="arquivo")
    fiscalizacoes = relationship("ArquivoFiscalizacao", back_populates="arquivo")
    analises = relationship("ArquivoAnalise", back_populates="arquivo")

    __table_args__ = (
        CheckConstraint("tamanho_bytes > 0", name="tamanho_valido"),
    )

