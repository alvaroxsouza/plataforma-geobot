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

    arquivo_id = Column(BigInteger, ForeignKey("arquivos.id", ondelete="CASCADE"), primary_key=True)
    analise_id = Column(BigInteger, ForeignKey("analises.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    arquivo = relationship("Arquivo", back_populates="analises")
    analise = relationship("Analise", back_populates="arquivos")
"""
Modelo de usuário do sistema
"""
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, SmallInteger, 
    String, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base


class Usuario(Base):
    """Modelo de usuário do sistema"""
    __tablename__ = "usuarios"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    data_ultimo_login = Column(DateTime(timezone=True))
    tentativas_login = Column(SmallInteger, default=0, nullable=False)
    bloqueado_ate = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True))

    # Relacionamentos
    grupos = relationship("UsuarioGrupo", back_populates="usuario")
    denuncias = relationship("Denuncia", back_populates="usuario")
    fiscalizacoes = relationship("Fiscalizacao", back_populates="fiscal", foreign_keys="Fiscalizacao.fiscal_id")

    __table_args__ = (
        CheckConstraint("cpf ~ '^\\d{11}$'", name="cpf_valido"),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="email_valido"),
        CheckConstraint("tentativas_login >= 0 AND tentativas_login <= 5", name="tentativas_validas"),
    )

