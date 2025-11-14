"""
Modelo de associação Many-to-Many entre Usuário e Fiscalização
"""
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.geobot_plataforma_backend.core.database import Base


class UsuarioFiscalizacao(Base):
    """
    Tabela de associação Many-to-Many entre Usuário e Fiscalização.
    
    Permite que uma fiscalização tenha múltiplos fiscais atribuídos
    e que um fiscal possa trabalhar em múltiplas fiscalizações.
    """
    __tablename__ = "usuario_fiscalizacao"
    __table_args__ = {'schema': 'geobot'}

    usuario_id = Column(
        BigInteger,
        ForeignKey("geobot.usuarios.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    fiscalizacao_id = Column(
        BigInteger,
        ForeignKey("geobot.fiscalizacoes.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    papel = Column(
        String(50),
        nullable=True,
        comment="Papel do fiscal nesta fiscalização (ex: responsável, auxiliar)"
    )
    data_atribuicao = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="fiscalizacoes_atribuidas")
    fiscalizacao = relationship("Fiscalizacao", back_populates="fiscais_atribuidos")

    def __repr__(self):
        return f"<UsuarioFiscalizacao(usuario_id={self.usuario_id}, fiscalizacao_id={self.fiscalizacao_id}, papel={self.papel})>"
