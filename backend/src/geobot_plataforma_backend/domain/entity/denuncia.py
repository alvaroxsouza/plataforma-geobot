"""
Modelo de denúncia
"""
from sqlalchemy import (
    BigInteger, Column, DateTime, Enum, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base
from .enums import StatusDenuncia, CategoriaDenuncia, Prioridade


class Denuncia(Base):
    """Modelo de denúncia"""
    __tablename__ = "denuncias"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    endereco_id = Column(BigInteger, ForeignKey("enderecos.id", ondelete="RESTRICT"), nullable=False)
    status = Column(Enum(StatusDenuncia, name="status_denuncia"), default=StatusDenuncia.PENDENTE, nullable=False)
    categoria = Column(Enum(CategoriaDenuncia, name="categoria_denuncia"), nullable=False)
    prioridade = Column(Enum(Prioridade, name="prioridade"), default=Prioridade.MEDIA, nullable=False)
    observacao = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="denuncias")
    endereco = relationship("Endereco", back_populates="denuncias")
    fiscalizacoes = relationship("Fiscalizacao", back_populates="denuncia")
    arquivos = relationship("ArquivoDenuncia", back_populates="denuncia")

