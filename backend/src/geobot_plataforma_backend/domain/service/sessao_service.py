"""
Serviço para gerenciamento de sessões de usuário
"""
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
import secrets

from src.geobot_plataforma_backend.core.config import settings
from src.geobot_plataforma_backend.domain.entity.sessao import Sessao
from src.geobot_plataforma_backend.domain.repository.sessao_repository import SessaoRepository


class SessaoService:
    """Serviço para gerenciar sessões de usuários"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = SessaoRepository(db)
        self.jwt_expiration_minutes = settings.get('jwt_expiration_minutes', 60)
        self.refresh_token_expiration_days = settings.get('refresh_token_expiration_days', 7)
        self.max_sessoes_simultaneas = settings.get('max_sessoes_simultaneas', 5)

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Cria hash seguro do token
        
        Args:
            token: Token a ser hashado
            
        Returns:
            Hash SHA256 do token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    def criar_sessao(
        self,
        usuario_id: int,
        token: str,
        refresh_token: str,
        device_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Sessao:
        """
        Cria uma nova sessão para um usuário
        
        Args:
            usuario_id: ID do usuário
            token: Token JWT
            refresh_token: Refresh token
            device_name: Nome do dispositivo (ex: iPhone, Firefox)
            ip_address: Endereço IP da sessão
            user_agent: User-Agent do navegador/app
            
        Returns:
            Sessao criada
        """
        now = datetime.now(timezone.utc)
        expira_em = now + timedelta(minutes=self.jwt_expiration_minutes)
        refresh_expira_em = now + timedelta(days=self.refresh_token_expiration_days)

        sessao = Sessao(
            usuario_id=usuario_id,
            token_hash=self._hash_token(token),
            refresh_token_hash=self._hash_token(refresh_token),
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            expira_em=expira_em,
            refresh_token_expira_em=refresh_expira_em,
            proxima_renovacao_permitida_em=now + timedelta(minutes=5),  # Permite renovar após 5 minutos
            ultima_atividade=now
        )

        return self.repository.criar(sessao)

    def validar_sessao(self, token_hash: str) -> Optional[Sessao]:
        """
        Valida se uma sessão está ativa
        
        Args:
            token_hash: Hash do token a validar
            
        Returns:
            Sessao se válida, None caso contrário
        """
        sessao = self.repository.buscar_por_token_hash(token_hash)
        
        if not sessao or not sessao.esta_ativa():
            return None

        # Atualiza última atividade
        sessao.registrar_atividade()
        self.repository.atualizar(sessao)
        
        return sessao

    def gerar_refresh_token(self) -> str:
        """Gera um novo refresh token seguro"""
        return secrets.token_urlsafe(32)

    def pode_renovar_token(self, sessao: Sessao) -> Tuple[bool, str]:
        """
        Verifica se a sessão pode renovar seu token
        
        Args:
            sessao: Sessão a verificar
            
        Returns:
            Tupla (pode_renovar, motivo)
        """
        if not sessao.esta_ativa():
            return False, "Sessão inativa ou expirada"

        now = datetime.now(timezone.utc)

        # Verifica se o refresh token expirou
        if sessao.refresh_token_expira_em and now > sessao.refresh_token_expira_em:
            return False, "Refresh token expirado"

        # Verifica se pode renovar (rate limiting)
        if sessao.proxima_renovacao_permitida_em and now < sessao.proxima_renovacao_permitida_em:
            tempo_restante = int((sessao.proxima_renovacao_permitida_em - now).total_seconds())
            return False, f"Aguarde {tempo_restante} segundos para renovar o token"

        return True, ""

    def registrar_tentativa_renovacao(self, sessao: Sessao) -> None:
        """Registra uma tentativa de renovação de token"""
        sessao.tentativas_renovacao += 1
        sessao.proxima_renovacao_permitida_em = datetime.now(timezone.utc) + timedelta(minutes=5)
        self.repository.atualizar(sessao)

    def registrar_acesso_invalido(self, sessao: Sessao) -> None:
        """Registra uma tentativa de acesso inválido"""
        sessao.tentativas_acesso_invalido += 1
        self.repository.atualizar(sessao)

    def revogar_sessao(self, sessao_id: int, motivo: str = "Revogado") -> bool:
        """Revoga uma sessão específica"""
        return self.repository.revogar_sessao(sessao_id, motivo)

    def revogar_todas_usuario(self, usuario_id: int) -> int:
        """Revoga todas as sessões de um usuário"""
        return self.repository.revogar_todas_sessoes_usuario(usuario_id, "Todas revogadas pelo usuário")

    def revogar_outras_sessoes(self, usuario_id: int, sessao_id_manter: int) -> int:
        """
        Revoga todas as sessões de um usuário exceto uma
        
        Args:
            usuario_id: ID do usuário
            sessao_id_manter: ID da sessão para manter ativa
            
        Returns:
            Número de sessões revogadas
        """
        sessoes = self.repository.buscar_sessoes_ativas_usuario(usuario_id)
        contador = 0
        
        for sessao in sessoes:
            if sessao.id != sessao_id_manter:
                sessao.revogar("Revogada ao fazer login em outro dispositivo")
                self.repository.atualizar(sessao)
                contador += 1
        
        return contador

    def limpar_sessoes_usuario(self, usuario_id: int) -> None:
        """Remove todas as sessões expiradas de um usuário"""
        self.repository.limpar_sessoes_expiradas_usuario(usuario_id)

    def obter_sessoes_ativas(self, usuario_id: int) -> List[Sessao]:
        """Obtém todas as sessões ativas de um usuário"""
        return self.repository.buscar_sessoes_ativas_usuario(usuario_id)

    def verificar_limite_sessoes(self, usuario_id: int) -> Tuple[bool, Optional[Sessao]]:
        """
        Verifica se o usuário atingiu o limite de sessões simultâneas
        
        Returns:
            Tupla (atingiu_limite, sessao_mais_antiga_para_remover)
        """
        ativas = self.repository.contar_sessoes_ativas_usuario(usuario_id)
        
        if ativas < self.max_sessoes_simultaneas:
            return False, None

        # Se atingiu o limite, retorna a sessão mais antiga para possível remoção
        sessoes = self.repository.buscar_sessoes_ativas_usuario(usuario_id)
        if sessoes:
            return True, sessoes[-1]  # Última é a mais antiga
        
        return False, None

    def manter_sessao_ativa(self, usuario_id: int, sessao_uuid: str) -> bool:
        """
        Mantém uma sessão ativa ao registrar atividade
        
        Args:
            usuario_id: ID do usuário
            sessao_uuid: UUID da sessão
            
        Returns:
            True se atualizado com sucesso
        """
        sessao = self.repository.buscar_por_uuid(sessao_uuid)
        
        if not sessao or sessao.usuario_id != usuario_id or not sessao.esta_ativa():
            return False

        sessao.registrar_atividade()
        self.repository.atualizar(sessao)
        return True

    def gerar_relatorio_sessoes(self, usuario_id: int) -> dict:
        """
        Gera um relatório de todas as sessões do usuário
        
        Returns:
            Dicionário com informações das sessões
        """
        sessoes_ativas = self.repository.buscar_sessoes_ativas_usuario(usuario_id)
        sessoes_todas = self.repository.buscar_sessoes_usuario(usuario_id, ativas_apenas=False)

        return {
            'total_sessoes': len(sessoes_todas),
            'sessoes_ativas': len(sessoes_ativas),
            'sessoes': [s.to_dict() for s in sessoes_todas]
        }
