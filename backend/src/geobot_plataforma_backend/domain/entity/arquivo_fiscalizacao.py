"""
Tabela de associação arquivo-fiscalização
"""
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.geobot_plataforma_backend.core.database import Base


class ArquivoFiscalizacao(Base):
    """Tabela de associação arquivo-fiscalização"""
    __tablename__ = "arquivos_fiscalizacao"
    __table_args__ = {'schema': 'geobot'}

    arquivo_id = Column(BigInteger, ForeignKey("geobot.arquivos.id", ondelete="CASCADE"), primary_key=True)
    fiscalizacao_id = Column(BigInteger, ForeignKey("geobot.fiscalizacoes.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    arquivo = relationship("Arquivo", back_populates="fiscalizacoes")
    fiscalizacao = relationship("Fiscalizacao", back_populates="arquivos")

