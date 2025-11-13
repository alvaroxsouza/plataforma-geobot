"""
Modelo de Sessão do usuário para gerenciar logins e tokens ativos
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, String, BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.geobot_plataforma_backend.core.database import Base


class Sessao(Base):
    """Modelo de sessão de usuário - rastreia logins ativos e tokens"""
    __tablename__ = "sessoes"
    __table_args__ = (
        {'schema': 'geobot'}
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    usuario_id = Column(BigInteger, ForeignKey('geobot.usuarios.id'), nullable=False)
    
    # Token JWT principal (armazenado como hash)
    token_hash = Column(String(255), unique=True, nullable=False)
    
    # Refresh token (armazenado como hash)
    refresh_token_hash = Column(String(255), unique=True, nullable=True)
    
    # Informações da sessão
    device_name = Column(String(255), nullable=True)  # ex: "iPhone 12", "Firefox on Windows"
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    criada_em = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    ultima_atividade = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    expira_em = Column(DateTime(timezone=True), nullable=False)  # Quando o token expira
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    revogada_em = Column(DateTime(timezone=True), nullable=True)
    motivo_revogacao = Column(String(255), nullable=True)
    
    # Refresh info
    refresh_token_expira_em = Column(DateTime(timezone=True), nullable=True)
    proxima_renovacao_permitida_em = Column(DateTime(timezone=True), nullable=True)
    
    # Logs
    tentativas_renovacao = Column(BigInteger, default=0, nullable=False)
    tentativas_acesso_invalido = Column(BigInteger, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento
    usuario = relationship("Usuario", backref="sessoes")

    def esta_ativa(self) -> bool:
        """Verifica se a sessão está ativa e não expirou"""
        if not self.ativa:
            return False
        
        now = datetime.now(timezone.utc)
        
        if self.revogada_em and now >= self.revogada_em:
            return False
        
        if self.expira_em and now >= self.expira_em:
            return False
        
        return True

    def registrar_atividade(self) -> None:
        """Atualiza o timestamp da última atividade"""
        self.ultima_atividade = datetime.now(timezone.utc)

    def revogar(self, motivo: str = "Revogado pelo usuário") -> None:
        """Revoga a sessão"""
        self.ativa = False
        self.revogada_em = datetime.now(timezone.utc)
        self.motivo_revogacao = motivo

    def to_dict(self, incluir_tokens=False) -> dict:
        """Converte a sessão para dicionário"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'usuario_id': self.usuario_id,
            'device_name': self.device_name,
            'ip_address': self.ip_address,
            'ativa': self.ativa,
            'criada_em': self.criada_em.isoformat() if self.criada_em else None,
            'ultima_atividade': self.ultima_atividade.isoformat() if self.ultima_atividade else None,
            'expira_em': self.expira_em.isoformat() if self.expira_em else None,
            'tempo_restante_segundos': int((self.expira_em - datetime.now(timezone.utc)).total_seconds()) if self.expira_em and self.esta_ativa() else 0,
        }
