"""Serviço de fiscalização com controle de autorização"""
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid as uuid_lib

from src.geobot_plataforma_backend.domain.entity.fiscalizacao import Fiscalizacao
from src.geobot_plataforma_backend.domain.entity.denuncia import Denuncia
from src.geobot_plataforma_backend.domain.entity.usuario import Usuario
from src.geobot_plataforma_backend.domain.entity.enums import StatusFiscalizacao
from src.geobot_plataforma_backend.domain.repository.usuario_repository import UsuarioRepository


class AutorizacaoError(Exception):
    """Erro de autorização"""


class FiscalizacaoService:
    """Serviço para operações de fiscalização"""

    def __init__(self, db: Session):
        self.db = db
        self.usuario_repository = UsuarioRepository(db)

    def _verificar_usuario_ativo(self, usuario: Usuario) -> None:
        """Verifica se o usuário está ativo"""
        if not usuario.ativo:
            raise AutorizacaoError("Usuário inativo. Entre em contato com o administrador")

    def _verificar_permissao_admin_fiscal(self, usuario: Usuario) -> bool:
        """Verifica se usuário é admin ou fiscal"""
        # TODO: Implementar verificação real de grupos/roles quando disponível
        # Por enquanto, retorna True para desenvolvimento
        return True

    def criar_fiscalizacao(
        self, 
        denuncia_id: int,
        observacoes: Optional[str],
        usuario_id: int
    ) -> Fiscalizacao:
        """Cria uma nova fiscalização. Atribui ao usuário atual como fiscal."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        # Verificar se a denúncia existe
        denuncia = self.db.query(Denuncia).filter(Denuncia.id == denuncia_id).first()
        if not denuncia:
            raise ValueError("Denúncia não encontrada")

        # Gerar código único
        codigo = f"FISC-{uuid_lib.uuid4().hex[:8].upper()}"

        fiscalizacao = Fiscalizacao(
            denuncia_id=denuncia_id,
            fiscal_id=usuario_id,
            codigo=codigo,
            observacoes=observacoes,
            status=StatusFiscalizacao.AGUARDANDO
        )
        
        self.db.add(fiscalizacao)
        self.db.commit()
        self.db.refresh(fiscalizacao)
        
        return fiscalizacao

    def listar_fiscalizacoes(
        self,
        usuario_id: int,
        status_filter: Optional[StatusFiscalizacao] = None,
        fiscal_id_filter: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Fiscalizacao]:
        """Lista fiscalizações com filtros."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        query = self.db.query(Fiscalizacao)
        
        if status_filter:
            query = query.filter(Fiscalizacao.status == status_filter)
        
        if fiscal_id_filter:
            query = query.filter(Fiscalizacao.fiscal_id == fiscal_id_filter)
        
        return query.limit(limit).offset(offset).all()

    def listar_minhas_fiscalizacoes(
        self,
        usuario_id: int,
        status_filter: Optional[StatusFiscalizacao] = None
    ) -> List[Fiscalizacao]:
        """Lista fiscalizações do fiscal autenticado."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        query = self.db.query(Fiscalizacao).filter(Fiscalizacao.fiscal_id == usuario_id)
        
        if status_filter:
            query = query.filter(Fiscalizacao.status == status_filter)
        
        return query.all()

    def buscar_fiscalizacao(self, fiscalizacao_id: int, usuario_id: int) -> Fiscalizacao:
        """Busca uma fiscalização específica."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        fiscalizacao = self.db.query(Fiscalizacao).filter(Fiscalizacao.id == fiscalizacao_id).first()
        if not fiscalizacao:
            raise ValueError("Fiscalização não encontrada")

        # Verificar permissão: fiscal atribuído ou admin
        if fiscalizacao.fiscal_id != usuario_id and not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para visualizar esta fiscalização")

        return fiscalizacao

    def atribuir_fiscal(
        self,
        fiscalizacao_id: int,
        novo_fiscal_id: int,
        usuario_id: int
    ) -> Fiscalizacao:
        """Atribui um fiscal a uma fiscalização. Requer permissão admin."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        # Por enquanto, qualquer usuário autenticado pode atribuir
        # TODO: Ajustar conforme regras de negócio
        if not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para atribuir fiscais")

        fiscalizacao = self.db.query(Fiscalizacao).filter(Fiscalizacao.id == fiscalizacao_id).first()
        if not fiscalizacao:
            raise ValueError("Fiscalização não encontrada")

        # Verificar se o novo fiscal existe
        novo_fiscal = self.usuario_repository.buscar_por_id(novo_fiscal_id)
        if not novo_fiscal:
            raise ValueError("Fiscal não encontrado")

        fiscalizacao.fiscal_id = novo_fiscal_id
        self.db.add(fiscalizacao)
        self.db.commit()
        self.db.refresh(fiscalizacao)

        return fiscalizacao

    def atualizar_status(
        self,
        fiscalizacao_id: int,
        novo_status: StatusFiscalizacao,
        usuario_id: int
    ) -> Fiscalizacao:
        """Atualiza o status de uma fiscalização."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        fiscalizacao = self.db.query(Fiscalizacao).filter(Fiscalizacao.id == fiscalizacao_id).first()
        if not fiscalizacao:
            raise ValueError("Fiscalização não encontrada")

        # Verificar permissão: fiscal atribuído ou admin
        if fiscalizacao.fiscal_id != usuario_id and not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para atualizar esta fiscalização")

        fiscalizacao.status = novo_status
        self.db.add(fiscalizacao)
        self.db.commit()
        self.db.refresh(fiscalizacao)

        return fiscalizacao
