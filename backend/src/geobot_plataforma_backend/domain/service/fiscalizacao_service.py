"""Serviço de fiscalização com controle de autorização"""
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid as uuid_lib

from src.geobot_plataforma_backend.domain.entity.fiscalizacao import Fiscalizacao
from src.geobot_plataforma_backend.domain.entity.denuncia import Denuncia
from src.geobot_plataforma_backend.domain.entity.usuario import Usuario
from src.geobot_plataforma_backend.domain.entity.usuario_fiscalizacao import UsuarioFiscalizacao
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
        usuario_id: int,
        fiscais_ids: Optional[List[int]] = None
    ) -> Fiscalizacao:
        """
        Cria uma nova fiscalização e atribui fiscais.
        
        Args:
            denuncia_id: ID da denúncia
            observacoes: Observações sobre a fiscalização
            usuario_id: ID do usuário criador (será atribuído como fiscal responsável se fiscais_ids for None)
            fiscais_ids: Lista de IDs dos fiscais a serem atribuídos (opcional)
        
        Returns:
            Fiscalização criada com fiscais atribuídos
        """
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        # Verificar se a denúncia existe
        denuncia = self.db.query(Denuncia).filter(Denuncia.id == denuncia_id).first()
        if not denuncia:
            raise ValueError("Denúncia não encontrada")

        # VALIDAÇÃO 1-PARA-1: Verificar se a denúncia já está em fiscalização ou foi concluída
        from src.geobot_plataforma_backend.domain.entity.enums import StatusDenuncia
        if denuncia.status not in [StatusDenuncia.PENDENTE, StatusDenuncia.EM_ANALISE]:
            raise ValueError("Esta denúncia já está em processo de fiscalização ou foi concluída.")

        # Verificar se já existe uma fiscalização ativa para esta denúncia
        fiscalizacao_existente = self.db.query(Fiscalizacao).filter(
            Fiscalizacao.denuncia_id == denuncia_id,
            Fiscalizacao.status.in_([StatusFiscalizacao.AGUARDANDO, StatusFiscalizacao.EM_ANDAMENTO])
        ).first()
        if fiscalizacao_existente:
            raise ValueError("Esta denúncia já possui uma fiscalização ativa.")

        # Gerar código único
        codigo = f"FISC-{uuid_lib.uuid4().hex[:8].upper()}"

        fiscalizacao = Fiscalizacao(
            denuncia_id=denuncia_id,
            codigo=codigo,
            observacoes=observacoes,
            status=StatusFiscalizacao.AGUARDANDO
        )
        
        # Atualizar status da denúncia para EM_FISCALIZACAO
        from src.geobot_plataforma_backend.domain.entity.enums import StatusDenuncia
        denuncia.status = StatusDenuncia.EM_FISCALIZACAO
        
        self.db.add(fiscalizacao)
        self.db.flush()  # Flush para obter o ID da fiscalização
        
        # Atribuir fiscais
        if fiscais_ids:
            # Atribuir os fiscais especificados (primeiro como responsável, resto como auxiliares)
            for idx, fiscal_id in enumerate(fiscais_ids):
                fiscal = self.usuario_repository.buscar_por_id(fiscal_id)
                if not fiscal:
                    raise ValueError(f"Fiscal com ID {fiscal_id} não encontrado")
                
                papel = "responsavel" if idx == 0 else "auxiliar"
                atribuicao = UsuarioFiscalizacao(
                    usuario_id=fiscal_id,
                    fiscalizacao_id=fiscalizacao.id,
                    papel=papel
                )
                self.db.add(atribuicao)
        else:
            # Se nenhum fiscal especificado, atribuir o usuário criador como responsável
            atribuicao = UsuarioFiscalizacao(
                usuario_id=usuario_id,
                fiscalizacao_id=fiscalizacao.id,
                papel="responsavel"
            )
            self.db.add(atribuicao)
        self.db.add(denuncia)
        self.db.commit()
        # Não fazer refresh para evitar problemas com relacionamentos
        # O objeto já tem os atributos necessários após o commit
        
        return fiscalizacao

    def listar_fiscalizacoes(
        self,
        usuario_id: int,
        status_filter: Optional[StatusFiscalizacao] = None,
        fiscal_id_filter: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Fiscalizacao]:
        """Lista fiscalizações com filtros. Agora filtra por fiscais através do relacionamento M-para-M."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        query = self.db.query(Fiscalizacao)
        
        if status_filter:
            query = query.filter(Fiscalizacao.status == status_filter)
        
        # Filtrar por fiscal através da tabela de associação
        if fiscal_id_filter:
            query = query.join(UsuarioFiscalizacao).filter(
                UsuarioFiscalizacao.usuario_id == fiscal_id_filter
            )
        
        return query.limit(limit).offset(offset).all()

    def listar_minhas_fiscalizacoes(
        self,
        usuario_id: int,
        status_filter: Optional[StatusFiscalizacao] = None
    ) -> List[Fiscalizacao]:
        """Lista fiscalizações onde o usuário está atribuído como fiscal."""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        # Query através da tabela de associação
        query = self.db.query(Fiscalizacao).join(UsuarioFiscalizacao).filter(
            UsuarioFiscalizacao.usuario_id == usuario_id
        )
        
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

        # Verificar permissão: fiscal atribuído (qualquer papel) ou admin
        fiscal_ids = [f.id for f in fiscalizacao.fiscais]
        if usuario_id not in fiscal_ids and not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para visualizar esta fiscalização")

        return fiscalizacao

    def adicionar_fiscal(
        self,
        fiscalizacao_id: int,
        novo_fiscal_id: int,
        usuario_id: int,
        papel: str = "auxiliar"
    ) -> Fiscalizacao:
        """
        Adiciona um fiscal a uma fiscalização existente. Requer permissão admin.
        
        Args:
            fiscalizacao_id: ID da fiscalização
            novo_fiscal_id: ID do fiscal a adicionar
            usuario_id: ID do usuário que está fazendo a operação
            papel: "responsavel" ou "auxiliar" (padrão: auxiliar)
        """
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        if not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para atribuir fiscais")

        fiscalizacao = self.db.query(Fiscalizacao).filter(Fiscalizacao.id == fiscalizacao_id).first()
        if not fiscalizacao:
            raise ValueError("Fiscalização não encontrada")

        # Verificar se o novo fiscal existe
        novo_fiscal = self.usuario_repository.buscar_por_id(novo_fiscal_id)
        if not novo_fiscal:
            raise ValueError("Fiscal não encontrado")

        # Verificar se o fiscal já está atribuído
        atribuicao_existente = self.db.query(UsuarioFiscalizacao).filter(
            UsuarioFiscalizacao.usuario_id == novo_fiscal_id,
            UsuarioFiscalizacao.fiscalizacao_id == fiscalizacao_id
        ).first()
        
        if atribuicao_existente:
            raise ValueError("Este fiscal já está atribuído a esta fiscalização")

        # Criar nova atribuição
        atribuicao = UsuarioFiscalizacao(
            usuario_id=novo_fiscal_id,
            fiscalizacao_id=fiscalizacao_id,
            papel=papel
        )
        self.db.add(atribuicao)
        self.db.commit()
        self.db.refresh(fiscalizacao)

        return fiscalizacao

    def remover_fiscal(
        self,
        fiscalizacao_id: int,
        fiscal_id: int,
        usuario_id: int
    ) -> Fiscalizacao:
        """
        Remove um fiscal de uma fiscalização. Requer permissão admin.
        Não permite remover se for o único fiscal responsável.
        """
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        if not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para remover fiscais")

        fiscalizacao = self.db.query(Fiscalizacao).filter(Fiscalizacao.id == fiscalizacao_id).first()
        if not fiscalizacao:
            raise ValueError("Fiscalização não encontrada")

        # Buscar atribuição
        atribuicao = self.db.query(UsuarioFiscalizacao).filter(
            UsuarioFiscalizacao.usuario_id == fiscal_id,
            UsuarioFiscalizacao.fiscalizacao_id == fiscalizacao_id
        ).first()
        
        if not atribuicao:
            raise ValueError("Este fiscal não está atribuído a esta fiscalização")

        # Verificar se é o único responsável
        total_fiscais = self.db.query(UsuarioFiscalizacao).filter(
            UsuarioFiscalizacao.fiscalizacao_id == fiscalizacao_id
        ).count()
        
        if total_fiscais == 1:
            raise ValueError("Não é possível remover o único fiscal da fiscalização")

        self.db.delete(atribuicao)
        self.db.commit()
        self.db.refresh(fiscalizacao)

        return fiscalizacao

    def atualizar_status(
        self,
        fiscalizacao_id: int,
        novo_status: StatusFiscalizacao,
        usuario_id: int
    ) -> Fiscalizacao:
        """Atualiza o status de uma fiscalização.
        
        SINCRONIZAÇÃO: Quando a fiscalização é concluída, a denúncia associada
        também é automaticamente marcada como concluída.
        """
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        self._verificar_usuario_ativo(usuario)

        fiscalizacao = self.db.query(Fiscalizacao).filter(Fiscalizacao.id == fiscalizacao_id).first()
        if not fiscalizacao:
            raise ValueError("Fiscalização não encontrada")

        # Verificar permissão: fiscal atribuído (qualquer papel) ou admin
        fiscal_ids = [f.id for f in fiscalizacao.fiscais]
        if usuario_id not in fiscal_ids and not self._verificar_permissao_admin_fiscal(usuario):
            raise AutorizacaoError("Usuário não tem permissão para atualizar esta fiscalização")

        # Atualizar status da fiscalização
        fiscalizacao.status = novo_status
        self.db.add(fiscalizacao)
        
        # SINCRONIZAÇÃO: Se a fiscalização foi concluída, concluir a denúncia também
        if novo_status == StatusFiscalizacao.CONCLUIDA:
            denuncia = self.db.query(Denuncia).filter(Denuncia.id == fiscalizacao.denuncia_id).first()
            if denuncia:
                from src.geobot_plataforma_backend.domain.entity.enums import StatusDenuncia
                denuncia.status = StatusDenuncia.CONCLUIDA
                self.db.add(denuncia)
        
        self.db.commit()
        self.db.refresh(fiscalizacao)

        return fiscalizacao
