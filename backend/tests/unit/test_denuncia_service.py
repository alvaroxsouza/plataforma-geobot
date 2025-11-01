"""
Testes unitários dos serviços de denúncia.

Estes testes focam na lógica de negócio isolada, sem depender de HTTP.
"""
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.domain.service.denuncia_service import (
    DenunciaService,
    AutorizacaoError
)
from src.geobot_plataforma_backend.api.dtos import DenunciaCriarDTO
from src.geobot_plataforma_backend.domain.entity import (
    Usuario,
    Denuncia,
    StatusDenuncia,
    CategoriaDenuncia
)


class TestDenunciaServiceCriar:
    """Testes do método criar_denuncia"""
    
    def test_criar_denuncia_usuario_ativo(self, db_session: Session):
        """Teste de criação de denúncia com usuário ativo"""
        # Arrange
        service = DenunciaService(db_session)
        
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Teste",
            logradouro="Rua Teste, 123",
            bairro="Centro",
            cidade="Cidade",
            estado="SP",
            cep="12345678",
            latitude=-23.5505,
            longitude=-46.6333
        )
        
        usuario_id = 1
        
        # Act
        resultado = service.criar_denuncia(dto, usuario_id)
        
        # Assert
        assert resultado is not None
        assert resultado.id is not None
        assert resultado.status == StatusDenuncia.PENDENTE
        assert resultado.denunciante_id == usuario_id
    
    def test_criar_denuncia_usuario_inativo(self, db_session: Session):
        """Teste de criação de denúncia com usuário inativo"""
        from src.geobot_plataforma_backend.domain.repository.usuario_repository import UsuarioRepository
        
        # Criar usuário inativo
        usuario_repo = UsuarioRepository(db_session)
        usuario = Usuario(
            cpf="12345678901",
            nome="Usuário Inativo",
            email="inativo@exemplo.com",
            senha_hash="hash",
            ativo=False
        )
        db_session.add(usuario)
        db_session.commit()
        
        # Tentar criar denúncia
        service = DenunciaService(db_session)
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Teste",
            logradouro="Rua Teste",
            bairro="Centro",
            cidade="Cidade",
            estado="SP",
            cep="12345678"
        )
        
        with pytest.raises(AutorizacaoError, match="inativo"):
            service.criar_denuncia(dto, usuario.id)


class TestDenunciaServiceListar:
    """Testes dos métodos de listagem"""
    
    def test_listar_minhas_denuncias_vazio(self, db_session: Session):
        """Teste de listagem quando usuário não tem denúncias"""
        service = DenunciaService(db_session)
        
        resultado = service.listar_minhas_denuncias(usuario_id=999)
        
        assert isinstance(resultado, list)
        assert len(resultado) == 0
    
    def test_listar_minhas_denuncias_com_dados(self, db_session: Session):
        """Teste de listagem quando usuário tem denúncias"""
        # Criar usuário
        usuario = Usuario(
            cpf="12345678901",
            nome="Teste",
            email="teste@exemplo.com",
            senha_hash="hash"
        )
        db_session.add(usuario)
        db_session.flush()
        
        # Criar denúncia
        service = DenunciaService(db_session)
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Teste",
            logradouro="Rua Teste",
            bairro="Centro",
            cidade="Cidade",
            estado="SP",
            cep="12345678"
        )
        service.criar_denuncia(dto, usuario.id)
        
        # Listar
        resultado = service.listar_minhas_denuncias(usuario.id)
        
        assert len(resultado) == 1
        assert resultado[0].denunciante_id == usuario.id


class TestDenunciaServiceBuscar:
    """Testes do método buscar_denuncia"""
    
    def test_buscar_denuncia_existente(self, db_session: Session):
        """Teste de busca de denúncia existente"""
        # Criar denúncia
        usuario = Usuario(
            cpf="12345678901",
            nome="Teste",
            email="teste@exemplo.com",
            senha_hash="hash"
        )
        db_session.add(usuario)
        db_session.flush()
        
        service = DenunciaService(db_session)
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Teste",
            logradouro="Rua Teste",
            bairro="Centro",
            cidade="Cidade",
            estado="SP",
            cep="12345678"
        )
        denuncia = service.criar_denuncia(dto, usuario.id)
        
        # Buscar
        resultado = service.buscar_denuncia(denuncia.id, usuario.id)
        
        assert resultado is not None
        assert resultado.id == denuncia.id
    
    def test_buscar_denuncia_inexistente(self, db_session: Session):
        """Teste de busca de denúncia inexistente"""
        service = DenunciaService(db_session)
        
        with pytest.raises(ValueError, match="não encontrada"):
            service.buscar_denuncia(999, usuario_id=1)


class TestDenunciaServiceAtualizar:
    """Testes do método atualizar_denuncia"""
    
    def test_atualizar_denuncia_propria(self, db_session: Session):
        """Teste de atualização de denúncia própria"""
        # Criar denúncia
        usuario = Usuario(
            cpf="12345678901",
            nome="Teste",
            email="teste@exemplo.com",
            senha_hash="hash"
        )
        db_session.add(usuario)
        db_session.flush()
        
        service = DenunciaService(db_session)
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Descrição original",
            logradouro="Rua Teste",
            bairro="Centro",
            cidade="Cidade",
            estado="SP",
            cep="12345678"
        )
        denuncia = service.criar_denuncia(dto, usuario.id)
        
        # Atualizar
        from src.geobot_plataforma_backend.api.dtos import DenunciaAtualizarDTO
        dto_atualizar = DenunciaAtualizarDTO(descricao="Nova descrição")
        
        resultado = service.atualizar_denuncia(
            denuncia.id,
            dto_atualizar,
            usuario.id
        )
        
        assert resultado.descricao == "Nova descrição"
    
    def test_atualizar_denuncia_outro_usuario(self, db_session: Session):
        """Teste de tentativa de atualizar denúncia de outro usuário"""
        # Criar dois usuários
        usuario1 = Usuario(
            cpf="12345678901",
            nome="Usuário 1",
            email="usuario1@exemplo.com",
            senha_hash="hash"
        )
        usuario2 = Usuario(
            cpf="98765432100",
            nome="Usuário 2",
            email="usuario2@exemplo.com",
            senha_hash="hash"
        )
        db_session.add_all([usuario1, usuario2])
        db_session.flush()
        
        # Criar denúncia com usuário 1
        service = DenunciaService(db_session)
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Descrição",
            logradouro="Rua Teste",
            bairro="Centro",
            cidade="Cidade",
            estado="SP",
            cep="12345678"
        )
        denuncia = service.criar_denuncia(dto, usuario1.id)
        
        # Tentar atualizar com usuário 2
        from src.geobot_plataforma_backend.api.dtos import DenunciaAtualizarDTO
        dto_atualizar = DenunciaAtualizarDTO(descricao="Tentativa")
        
        with pytest.raises(AutorizacaoError):
            service.atualizar_denuncia(
                denuncia.id,
                dto_atualizar,
                usuario2.id
            )


class TestDenunciaServiceDeletar:
    """Testes do método deletar_denuncia"""
    
    def test_deletar_denuncia_propria(self, db_session: Session):
        """Teste de exclusão de denúncia própria"""
        # Criar denúncia
        usuario = Usuario(
            cpf="12345678901",
            nome="Teste",
            email="teste@exemplo.com",
            senha_hash="hash"
        )
        db_session.add(usuario)
        db_session.flush()
        
        service = DenunciaService(db_session)
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Descrição",
            logradouro="Rua Teste",
            bairro="Centro",
            cidade="Cidade",
            estado="SP",
            cep="12345678"
        )
        denuncia = service.criar_denuncia(dto, usuario.id)
        denuncia_id = denuncia.id
        
        # Deletar
        service.deletar_denuncia(denuncia_id, usuario.id)
        
        # Verificar que foi deletada
        with pytest.raises(ValueError):
            service.buscar_denuncia(denuncia_id, usuario.id)
