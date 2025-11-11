"""
Modelo de endereço
"""
from sqlalchemy import (
    BigInteger, Column, DateTime, Numeric, String, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base


class Endereco(Base):
    """Modelo de endereço"""
    __tablename__ = "enderecos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    logradouro = Column(String(255), nullable=False)
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    pais = Column(String(2), default="BR", nullable=False)
    cep = Column(String(8), nullable=False)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    denuncias = relationship("Denuncia", back_populates="endereco")

    __table_args__ = (
        CheckConstraint("cep ~ '^\\d{8}$'", name="cep_valido"),
        CheckConstraint("LENGTH(estado) = 2", name="uf_valida"),
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="latitude_valida"),
        CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="longitude_valida"),
        {'schema': 'geobot'}
    )

