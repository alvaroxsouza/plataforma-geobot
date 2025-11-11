"""
Tabela de associação arquivo-denúncia
"""
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.geobot_plataforma_backend.core.database import Base


class ArquivoDenuncia(Base):
    """Tabela de associação arquivo-denúncia"""
    __tablename__ = "arquivos_denuncia"
    __table_args__ = {'schema': 'geobot'}

    arquivo_id = Column(BigInteger, ForeignKey("geobot.arquivos.id", ondelete="CASCADE"), primary_key=True)
    denuncia_id = Column(BigInteger, ForeignKey("geobot.denuncias.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    arquivo = relationship("Arquivo", back_populates="denuncias")
    denuncia = relationship("Denuncia", back_populates="arquivos")

