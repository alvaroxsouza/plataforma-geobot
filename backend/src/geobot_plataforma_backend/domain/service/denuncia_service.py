"""Serviço de denúncias com controle de autorização"""
from typing import Optional, List
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.domain.entity.denuncia import Denuncia
from src.geobot_plataforma_backend.domain.entity.endereco import Endereco
from src.geobot_plataforma_backend.domain.entity.usuario import Usuario
from src.geobot_plataforma_backend.domain.entity.enums import (
    StatusDenuncia,
    Prioridade,
    CategoriaDenuncia,
)
from src.geobot_plataforma_backend.domain.repository.denuncia_repository import DenunciaRepository
from src.geobot_plataforma_backend.domain.repository.usuario_repository import UsuarioRepository
from src.geobot_plataforma_backend.api.dtos.denuncia_dto import (
    DenunciaCriarDTO,
    DenunciaAtualizarDTO,
    DenunciaResponseDTO,
)


class AutorizacaoError(Exception):
    """Erro de autorização"""


class DenunciaService:
    """Serviço para operações de denúncias"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = DenunciaRepository(db)
        self.usuario_repository = UsuarioRepository(db)

    def _verificar_usuario_ativo(self, usuario: Usuario) -> None:
        """Verifica se o usuário está ativo"""
        if not usuario.ativo:
            raise AutorizacaoError("Usuário inativo. Entre em contato com o administrador")

    def _verificar_permissao_admin_fiscal(self, usuario: Usuario) -> bool:
        """Verifica se usuário é admin ou fiscal"""
        # TODO: Implementar verificação real de grupos/roles quando disponível
        # Por enquanto, simples verificação de exemplo
        roles_autorizadas = {"admin", "fiscalizar", "gerenciar_usuarios"}

        # Aqui você faria: usuario.grupos -> roles
        # Exemplo simplificado:
        # for grupo in usuario.grupos:
        #     for role in grupo.grupo.roles:
        #         if role.role.nome in roles_autorizadas:
        #             return True
        # return False

        # Temporariamente retorna True para desenvolvimento
        return True

    def criar_denuncia(self, dados: DenunciaCriarDTO, usuario_id: int) -> DenunciaResponseDTO:
        """Cria uma nova denúncia. Qualquer usuário ativo pode criar denúncias."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        endereco = Endereco(
            logradouro=dados.logradouro,
            numero=dados.numero,
            complemento=dados.complemento,
            bairro=dados.bairro,
            cidade=dados.cidade,
            estado=dados.estado.upper(),
            cep=dados.cep.replace("-", ""),
            latitude=dados.latitude,
            longitude=dados.longitude,
        )
        endereco = self.repository.criar_endereco(endereco)

        denuncia = Denuncia(
            usuario_id=usuario_id,
            endereco_id=endereco.id,
            status=StatusDenuncia.PENDENTE,
            categoria=dados.categoria,
            prioridade=dados.prioridade,
            observacao=dados.observacao,
        )
        denuncia = self.repository.criar(denuncia)

        return DenunciaResponseDTO.from_entity(denuncia)

    def listar_minhas_denuncias(
        self,
        usuario_id: int,
        status: Optional[StatusDenuncia] = None,
    ) -> List[DenunciaResponseDTO]:
        """Lista denúncias do usuário atual."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        denuncias = self.repository.listar_por_usuario(usuario_id, status)
        return [DenunciaResponseDTO.from_entity(d) for d in denuncias]

    def listar_todas_denuncias(
        self,
        usuario_id: int,
        status: Optional[StatusDenuncia] = None,
    ) -> List[DenunciaResponseDTO]:
        """Lista todas as denúncias do sistema. Requer admin/fiscal."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        if not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para listar todas as denúncias")

        denuncias = self.repository.listar_todas(status)
        return [DenunciaResponseDTO.from_entity(d) for d in denuncias]

    def buscar_denuncia(self, denuncia_id: int, usuario_id: int) -> DenunciaResponseDTO:
        """Busca uma denúncia específica."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        denuncia = self.repository.buscar_por_id(denuncia_id)
        if not denuncia:
            raise ValueError("Denúncia não encontrada")

        if denuncia.usuario_id != usuario_id and not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para visualizar esta denúncia")

        return DenunciaResponseDTO.from_entity(denuncia)

    def atualizar_denuncia(
        self,
        denuncia_id: int,
        dados: DenunciaAtualizarDTO,
        usuario_id: int,
    ) -> DenunciaResponseDTO:
        """Atualiza uma denúncia. Apenas o criador pode atualizar (status PENDENTE)."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        denuncia = self.repository.buscar_por_id(denuncia_id)
        if not denuncia:
            raise ValueError("Denúncia não encontrada")

        if denuncia.usuario_id != usuario_id:
            raise AutorizacaoError("Apenas o criador pode atualizar a denúncia")

        if denuncia.status != StatusDenuncia.PENDENTE:
            raise ValueError("Apenas denúncias pendentes podem ser editadas")

        if dados.observacao is not None:
            denuncia.observacao = dados.observacao
        if dados.prioridade is not None:
            denuncia.prioridade = dados.prioridade

        denuncia = self.repository.atualizar(denuncia)
        return DenunciaResponseDTO.from_entity(denuncia)

    def deletar_denuncia(self, denuncia_id: int, usuario_id: int) -> bool:
        """Deleta uma denúncia. Apenas o criador (status PENDENTE)."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        denuncia = self.repository.buscar_por_id(denuncia_id)
        if not denuncia:
            raise ValueError("Denúncia não encontrada")

        if denuncia.usuario_id != usuario_id:
            raise AutorizacaoError("Apenas o criador pode deletar a denúncia")

        if denuncia.status != StatusDenuncia.PENDENTE:
            raise ValueError("Apenas denúncias pendentes podem ser deletadas")

        return self.repository.deletar(denuncia)

    def atualizar_status_denuncia(
        self,
        denuncia_id: int,
        novo_status: StatusDenuncia,
        usuario_id: int,
    ) -> DenunciaResponseDTO:
        """Atualiza o status de uma denúncia. Requer admin/fiscal."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        if not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Apenas admin/fiscal podem alterar status de denúncias")

        denuncia = self.repository.buscar_por_id(denuncia_id)
        if not denuncia:
            raise ValueError("Denúncia não encontrada")

        denuncia = self.repository.atualizar_status(denuncia, novo_status)
        return DenunciaResponseDTO.from_entity(denuncia)
