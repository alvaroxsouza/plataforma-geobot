"""
Testes unitários dos DTOs de denúncia.

Testa validações Pydantic e conversões.
"""
import pytest
from pydantic import ValidationError

from src.geobot_plataforma_backend.api.dtos import (
    DenunciaCriarDTO,
    DenunciaAtualizarDTO,
    DenunciaResponseDTO
)


class TestDenunciaCriarDTO:
    """Testes do DTO de criação de denúncia"""
    
    def test_criar_dto_valido(self):
        """Teste de criação com dados válidos"""
        dto = DenunciaCriarDTO(
            categoria="POLUICAO",
            descricao="Descarte irregular",
            logradouro="Rua Teste, 123",
            bairro="Centro",
            cidade="São Paulo",
            estado="SP",
            cep="12345678",
            latitude=-23.5505,
            longitude=-46.6333
        )
        
        assert dto.categoria == "POLUICAO"
        assert dto.estado == "SP"
        assert dto.cep == "12345678"
    
    def test_criar_dto_logradouro_vazio(self):
        """Teste de validação de logradouro vazio"""
        with pytest.raises(ValidationError) as exc_info:
            DenunciaCriarDTO(
                categoria="POLUICAO",
                descricao="Teste",
                logradouro="   ",  # Apenas espaços
                bairro="Centro",
                cidade="São Paulo",
                estado="SP",
                cep="12345678"
            )
        
        assert "logradouro" in str(exc_info.value).lower()
    
    def test_criar_dto_estado_invalido(self):
        """Teste de validação de estado inválido"""
        with pytest.raises(ValidationError) as exc_info:
            DenunciaCriarDTO(
                categoria="POLUICAO",
                descricao="Teste",
                logradouro="Rua Teste",
                bairro="Centro",
                cidade="São Paulo",
                estado="ABC",  # Estado inválido
                cep="12345678"
            )
        
        assert "estado" in str(exc_info.value).lower()
    
    def test_criar_dto_cep_invalido(self):
        """Teste de validação de CEP inválido"""
        with pytest.raises(ValidationError) as exc_info:
            DenunciaCriarDTO(
                categoria="POLUICAO",
                descricao="Teste",
                logradouro="Rua Teste",
                bairro="Centro",
                cidade="São Paulo",
                estado="SP",
                cep="123"  # CEP muito curto
            )
        
        assert "cep" in str(exc_info.value).lower()
    
    def test_criar_dto_categoria_invalida(self):
        """Teste de validação de categoria inválida"""
        with pytest.raises(ValidationError):
            DenunciaCriarDTO(
                categoria="CATEGORIA_INEXISTENTE",
                descricao="Teste",
                logradouro="Rua Teste",
                bairro="Centro",
                cidade="São Paulo",
                estado="SP",
                cep="12345678"
            )


class TestDenunciaAtualizarDTO:
    """Testes do DTO de atualização de denúncia"""
    
    def test_atualizar_dto_parcial(self):
        """Teste de atualização parcial (apenas alguns campos)"""
        dto = DenunciaAtualizarDTO(
            descricao="Nova descrição"
        )
        
        assert dto.descricao == "Nova descrição"
        assert dto.categoria is None
        assert dto.logradouro is None
    
    def test_atualizar_dto_todos_campos(self):
        """Teste de atualização com todos os campos"""
        dto = DenunciaAtualizarDTO(
            categoria="DESMATAMENTO",
            descricao="Descrição atualizada",
            logradouro="Nova Rua, 456",
            bairro="Novo Bairro",
            cidade="Nova Cidade",
            estado="RJ",
            cep="87654321",
            latitude=-22.9068,
            longitude=-43.1729
        )
        
        assert dto.categoria == "DESMATAMENTO"
        assert dto.estado == "RJ"
        assert dto.cep == "87654321"


class TestDenunciaResponseDTO:
    """Testes do DTO de resposta de denúncia"""
    
    def test_response_dto_from_entity(self, db_session):
        """Teste de conversão de entidade para DTO"""
        from src.geobot_plataforma_backend.domain.entity import (
            Denuncia,
            Endereco,
            Usuario,
            StatusDenuncia,
            CategoriaDenuncia
        )
        
        # Criar usuário
        usuario = Usuario(
            cpf="12345678901",
            nome="Teste",
            email="teste@exemplo.com",
            senha_hash="hash"
        )
        db_session.add(usuario)
        db_session.flush()
        
        # Criar endereço
        endereco = Endereco(
            logradouro="Rua Teste",
            bairro="Centro",
            cidade="São Paulo",
            estado="SP",
            cep="12345678"
        )
        db_session.add(endereco)
        db_session.flush()
        
        # Criar denúncia
        denuncia = Denuncia(
            categoria=CategoriaDenuncia.POLUICAO,
            descricao="Teste",
            status=StatusDenuncia.PENDENTE,
            denunciante_id=usuario.id,
            endereco_id=endereco.id
        )
        db_session.add(denuncia)
        db_session.commit()
        
        # Converter para DTO
        dto = DenunciaResponseDTO.model_validate(denuncia)
        
        assert dto.id == denuncia.id
        assert dto.uuid == str(denuncia.uuid)
        assert dto.categoria == denuncia.categoria.value
        assert dto.status == denuncia.status.value
        assert dto.denunciante_id == usuario.id
