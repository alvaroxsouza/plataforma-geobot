"""
Tabela de associação arquivo-análise
"""
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.geobot_plataforma_backend.core.database import Base
class ArquivoAnalise(Base):
    """Tabela de associação arquivo-análise"""
    __tablename__ = "arquivos_analise"
    __table_args__ = {'schema': 'geobot'}
    arquivo_id = Column(BigInteger, ForeignKey("geobot.arquivos.id", ondelete="CASCADE"), primary_key=True)
    analise_id = Column(BigInteger, ForeignKey("geobot.analises.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    # Relacionamentos
    arquivo = relationship("Arquivo", back_populates="analises")
    analise = relationship("Analise", back_populates="arquivos")
