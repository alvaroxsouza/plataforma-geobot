"""
Modelos SQLAlchemy do sistema
"""
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, Numeric, SmallInteger, String, Text, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.geobot_plataforma_backend.core.database import Base
from .enums import (
    StatusDenuncia, CategoriaDenuncia, Prioridade,
    StatusFiscalizacao, TipoAnalise
)


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


class Grupo(Base):
    """Modelo de grupo de usuários"""
    __tablename__ = "grupos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    usuarios = relationship("UsuarioGrupo", back_populates="grupo")
    roles = relationship("GrupoRole", back_populates="grupo")


class Role(Base):
    """Modelo de papéis/permissões"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    grupos = relationship("GrupoRole", back_populates="role")


class UsuarioGrupo(Base):
    """Tabela de associação usuário-grupo"""
    __tablename__ = "usuario_grupo"

    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="grupos")
    grupo = relationship("Grupo", back_populates="usuarios")


class GrupoRole(Base):
    """Tabela de associação grupo-role"""
    __tablename__ = "grupo_role"

    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    grupo = relationship("Grupo", back_populates="roles")
    role = relationship("Role", back_populates="grupos")


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
    )


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


class Fiscalizacao(Base):
    """Modelo de fiscalização"""
    __tablename__ = "fiscalizacoes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    denuncia_id = Column(BigInteger, ForeignKey("denuncias.id", ondelete="RESTRICT"), nullable=False)
    fiscal_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(StatusFiscalizacao, name="status_fiscalizacao"), default=StatusFiscalizacao.AGUARDANDO, nullable=False)
    data_inicializacao = Column(DateTime(timezone=True))
    data_conclusao = Column(DateTime(timezone=True))
    observacoes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    denuncia = relationship("Denuncia", back_populates="fiscalizacoes")
    fiscal = relationship("Usuario", back_populates="fiscalizacoes", foreign_keys="Fiscalizacao.fiscal_id")
    analises = relationship("Analise", back_populates="fiscalizacao")
    arquivos = relationship("ArquivoFiscalizacao", back_populates="fiscalizacao")

    __table_args__ = (
        CheckConstraint("data_conclusao IS NULL OR data_conclusao >= data_inicializacao", name="datas_validas"),
    )


class Analise(Base):
    """Modelo de análise de IA"""
    __tablename__ = "analises"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    fiscalizacao_id = Column(BigInteger, ForeignKey("fiscalizacoes.id", ondelete="CASCADE"), nullable=False)
    tipo_analise = Column(Enum(TipoAnalise, name="tipo_analise"), nullable=False)
    dados_json = Column(JSONB, default=dict, nullable=False)
    resultado_principal = Column(Text)
    confianca = Column(Numeric(5, 2))
    processado_em = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    fiscalizacao = relationship("Fiscalizacao", back_populates="analises")
    arquivos = relationship("ArquivoAnalise", back_populates="analise")

    __table_args__ = (
        CheckConstraint("confianca IS NULL OR (confianca >= 0 AND confianca <= 100)", name="confianca_valida"),
    )


class Arquivo(Base):
    """Modelo de arquivo"""
    __tablename__ = "arquivos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    tamanho_bytes = Column(BigInteger, nullable=False)
    tipo_mime = Column(String(100), nullable=False)
    extensao = Column(String(10), nullable=False)
    chave_storage = Column(String(500), unique=True, nullable=False)
    hash_checksum = Column(String(64), nullable=False)
    data_upload = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    denuncias = relationship("ArquivoDenuncia", back_populates="arquivo")
    fiscalizacoes = relationship("ArquivoFiscalizacao", back_populates="arquivo")
    analises = relationship("ArquivoAnalise", back_populates="arquivo")

    __table_args__ = (
        CheckConstraint("tamanho_bytes > 0", name="tamanho_valido"),
    )


class ArquivoDenuncia(Base):
    """Tabela de associação arquivo-denúncia"""
    __tablename__ = "arquivos_denuncia"

    arquivo_id = Column(BigInteger, ForeignKey("arquivos.id", ondelete="CASCADE"), primary_key=True)
    denuncia_id = Column(BigInteger, ForeignKey("denuncias.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    arquivo = relationship("Arquivo", back_populates="denuncias")
    denuncia = relationship("Denuncia", back_populates="arquivos")


class ArquivoFiscalizacao(Base):
    """Tabela de associação arquivo-fiscalização"""
    __tablename__ = "arquivos_fiscalizacao"

    arquivo_id = Column(BigInteger, ForeignKey("arquivos.id", ondelete="CASCADE"), primary_key=True)
    fiscalizacao_id = Column(BigInteger, ForeignKey("fiscalizacoes.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    arquivo = relationship("Arquivo", back_populates="fiscalizacoes")
    fiscalizacao = relationship("Fiscalizacao", back_populates="arquivos")


class ArquivoAnalise(Base):
    """Tabela de associação arquivo-análise"""
    __tablename__ = "arquivos_analise"

    arquivo_id = Column(BigInteger, ForeignKey("arquivos.id", ondelete="CASCADE"), primary_key=True)
    analise_id = Column(BigInteger, ForeignKey("analises.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relacionamentos
    arquivo = relationship("Arquivo", back_populates="analises")
    analise = relationship("Analise", back_populates="arquivos")

