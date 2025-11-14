"""Repository para operações de denúncia"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from src.geobot_plataforma_backend.domain.entity.denuncia import Denuncia
from src.geobot_plataforma_backend.domain.entity.endereco import Endereco
from src.geobot_plataforma_backend.domain.entity.enums import StatusDenuncia


class DenunciaRepository:
    """Repository para gerenciar operações de denúncias"""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, denuncia: Denuncia) -> Denuncia:
        """Cria uma nova denúncia"""
        self.db.add(denuncia)
        self.db.commit()
        self.db.refresh(denuncia)
        return denuncia

    def criar_endereco(self, endereco: Endereco) -> Endereco:
        """Cria um novo endereço"""
        self.db.add(endereco)
        self.db.commit()
        self.db.refresh(endereco)
        return endereco

    def buscar_por_id(self, denuncia_id: int) -> Optional[Denuncia]:
        """Busca denúncia por ID com relacionamentos"""
        return (
            self.db.query(Denuncia)
            .options(joinedload(Denuncia.usuario), joinedload(Denuncia.endereco))
            .filter(Denuncia.id == denuncia_id)
            .first()
        )

    def buscar_por_uuid(self, uuid: str) -> Optional[Denuncia]:
        """Busca denúncia por UUID"""
        return (
            self.db.query(Denuncia)
            .options(joinedload(Denuncia.usuario), joinedload(Denuncia.endereco))
            .filter(Denuncia.uuid == uuid)
            .first()
        )

    def listar_por_usuario(
        self,
        usuario_id: int,
        status: Optional[StatusDenuncia] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Denuncia]:
        """Lista denúncias de um usuário específico"""
        query = (
            self.db.query(Denuncia)
            .options(joinedload(Denuncia.usuario), joinedload(Denuncia.endereco))
            .filter(Denuncia.usuario_id == usuario_id)
        )

        if status:
            query = query.filter(Denuncia.status == status)

        return query.order_by(Denuncia.created_at.desc()).limit(limit).offset(offset).all()

    def listar_todas(
        self,
        status: Optional[StatusDenuncia] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Denuncia]:
        """Lista todas as denúncias (para admins/fiscais)"""
        query = self.db.query(Denuncia).options(
            joinedload(Denuncia.usuario), joinedload(Denuncia.endereco)
        )

        if status:
            query = query.filter(Denuncia.status == status)

        return query.order_by(Denuncia.created_at.desc()).limit(limit).offset(offset).all()

    def atualizar(self, denuncia: Denuncia) -> Denuncia:
        """Atualiza uma denúncia"""
        self.db.commit()
        self.db.refresh(denuncia)
        return denuncia

    def atualizar_status(self, denuncia: Denuncia, novo_status: StatusDenuncia) -> Denuncia:
        """Atualiza o status de uma denúncia"""
        denuncia.status = novo_status
        return self.atualizar(denuncia)

    def deletar(self, denuncia: Denuncia) -> bool:
        """Deleta uma denúncia (hard delete)"""
        self.db.delete(denuncia)
        self.db.commit()
        return True

    def contar_por_status(self, usuario_id: Optional[int] = None) -> dict:
        """Conta denúncias por status"""
        query = self.db.query(Denuncia.status, func.count(Denuncia.id))

        if usuario_id:
            query = query.filter(Denuncia.usuario_id == usuario_id)

        results = query.group_by(Denuncia.status).all()
        return {status.value: count for status, count in results}

    def contar_total(
        self, 
        usuario_id: Optional[int] = None, 
        status: Optional[StatusDenuncia] = None
    ) -> int:
        """Conta o total de denúncias com filtros opcionais"""
        query = self.db.query(func.count(Denuncia.id))

        if usuario_id:
            query = query.filter(Denuncia.usuario_id == usuario_id)

        if status:
            query = query.filter(Denuncia.status == status)

        return query.scalar() or 0
