"""
Modelo de papéis/permissões
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base


class Role(Base):
    """Modelo de papéis/permissões"""
    __tablename__ = "roles"
    __table_args__ = {'schema': 'geobot'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    grupos = relationship("GrupoRole", back_populates="role")

