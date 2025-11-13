"""
Repository para gerenciar operações de sessão no banco de dados
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.geobot_plataforma_backend.domain.entity.sessao import Sessao


class SessaoRepository:
    """Repository para a entidade Sessao"""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, sessao: Sessao) -> Sessao:
        """Cria uma nova sessão no banco"""
        self.db.add(sessao)
        self.db.commit()
        self.db.refresh(sessao)
        return sessao

    def buscar_por_uuid(self, uuid: str) -> Optional[Sessao]:
        """Busca uma sessão pelo UUID"""
        return self.db.query(Sessao).filter(Sessao.uuid == uuid).first()

    def buscar_por_id(self, sessao_id: int) -> Optional[Sessao]:
        """Busca uma sessão pelo ID"""
        return self.db.query(Sessao).filter(Sessao.id == sessao_id).first()

    def buscar_por_token_hash(self, token_hash: str) -> Optional[Sessao]:
        """Busca uma sessão pelo hash do token"""
        return self.db.query(Sessao).filter(Sessao.token_hash == token_hash).first()

    def buscar_por_refresh_token_hash(self, refresh_token_hash: str) -> Optional[Sessao]:
        """Busca uma sessão pelo hash do refresh token"""
        return self.db.query(Sessao).filter(Sessao.refresh_token_hash == refresh_token_hash).first()

    def buscar_sessoes_ativas_usuario(self, usuario_id: int) -> List[Sessao]:
        """Busca todas as sessões ativas de um usuário"""
        now = datetime.now(timezone.utc)
        return self.db.query(Sessao).filter(
            and_(
                Sessao.usuario_id == usuario_id,
                Sessao.ativa == True,
                Sessao.expira_em > now,
                or_(Sessao.revogada_em == None, Sessao.revogada_em > now)
            )
        ).order_by(Sessao.ultima_atividade.desc()).all()

    def buscar_sessoes_usuario(self, usuario_id: int, ativas_apenas: bool = False) -> List[Sessao]:
        """
        Busca sessões de um usuário
        
        Args:
            usuario_id: ID do usuário
            ativas_apenas: Se True, retorna apenas sessões ativas
        """
        query = self.db.query(Sessao).filter(Sessao.usuario_id == usuario_id)
        
        if ativas_apenas:
            now = datetime.now(timezone.utc)
            query = query.filter(
                and_(
                    Sessao.ativa == True,
                    Sessao.expira_em > now
                )
            )
        
        return query.order_by(Sessao.criada_em.desc()).all()

    def contar_sessoes_ativas_usuario(self, usuario_id: int) -> int:
        """Conta o número de sessões ativas de um usuário"""
        now = datetime.now(timezone.utc)
        return self.db.query(Sessao).filter(
            and_(
                Sessao.usuario_id == usuario_id,
                Sessao.ativa == True,
                Sessao.expira_em > now
            )
        ).count()

    def atualizar(self, sessao: Sessao) -> Sessao:
        """Atualiza uma sessão no banco"""
        self.db.merge(sessao)
        self.db.commit()
        self.db.refresh(sessao)
        return sessao

    def revogar_sessao(self, sessao_id: int, motivo: str = "Revogado") -> bool:
        """Revoga uma sessão"""
        sessao = self.buscar_por_id(sessao_id)
        if sessao:
            sessao.revogar(motivo)
            self.db.commit()
            return True
        return False

    def revogar_todas_sessoes_usuario(self, usuario_id: int, motivo: str = "Todas as sessões revogadas") -> int:
        """Revoga todas as sessões ativas de um usuário"""
        sessoes = self.buscar_sessoes_ativas_usuario(usuario_id)
        for sessao in sessoes:
            sessao.revogar(motivo)
        self.db.commit()
        return len(sessoes)

    def excluir_sessoes_expiradas(self) -> int:
        """Remove sessões expiradas do banco (mantém histórico por 30 dias)"""
        now = datetime.now(timezone.utc)
        from sqlalchemy import func
        from datetime import timedelta
        
        # Remove sessões expiradas há mais de 30 dias
        cutoff_date = now - timedelta(days=30)
        deleted = self.db.query(Sessao).filter(
            and_(
                Sessao.expira_em < cutoff_date,
                Sessao.ativa == False
            )
        ).delete()
        
        self.db.commit()
        return deleted

    def excluir_por_id(self, sessao_id: int) -> bool:
        """Exclui uma sessão"""
        sessao = self.buscar_por_id(sessao_id)
        if sessao:
            self.db.delete(sessao)
            self.db.commit()
            return True
        return False

    def limpar_sessoes_expiradas_usuario(self, usuario_id: int) -> int:
        """Remove todas as sessões expiradas de um usuário"""
        now = datetime.now(timezone.utc)
        deleted = self.db.query(Sessao).filter(
            and_(
                Sessao.usuario_id == usuario_id,
                Sessao.expira_em < now
            )
        ).delete()
        self.db.commit()
        return deleted
