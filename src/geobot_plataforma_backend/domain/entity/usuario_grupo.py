"""
Tabela de associação usuário-grupo
"""
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.geobot_plataforma_backend.core.database import Base


class UsuarioGrupo(Base):
    """Tabela de associação usuário-grupo"""
    __tablename__ = "usuario_grupo"

    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="grupos")
    grupo = relationship("Grupo", back_populates="usuarios")

