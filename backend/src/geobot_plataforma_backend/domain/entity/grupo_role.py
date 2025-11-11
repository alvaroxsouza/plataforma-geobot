"""
Tabela de associação grupo-role
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.geobot_plataforma_backend.core.database import Base


class GrupoRole(Base):
    """Tabela de associação grupo-role"""
    __tablename__ = "grupo_role"
    __table_args__ = {'schema': 'geobot'}

    grupo_id = Column(Integer, ForeignKey("geobot.grupos.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("geobot.roles.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    grupo = relationship("Grupo", back_populates="roles")
    role = relationship("Role", back_populates="grupos")

