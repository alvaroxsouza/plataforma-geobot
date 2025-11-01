"""
Testes de integração do sistema de denúncias.

Este módulo testa os endpoints de denúncias usando TestClient do FastAPI.
"""
import pytest
from fastapi.testclient import TestClient


class TestCriarDenuncia:
    """Testes de criação de denúncia"""
    
    def test_criar_denuncia_sucesso(
        self, 
        client: TestClient, 
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de criação de denúncia com dados válidos"""
        response = client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "uuid" in data
        assert data["categoria"] == denuncia_valida_dados["categoria"]
        assert data["descricao"] == denuncia_valida_dados["descricao"]
        assert data["status"] == "PENDENTE"
        assert data["denunciante_id"] == usuario_autenticado["usuario"]["id"]
    
    def test_criar_denuncia_sem_autenticacao(
        self, 
        client: TestClient,
        denuncia_valida_dados: dict
    ):
        """Teste de criação de denúncia sem autenticação"""
        response = client.post("/api/denuncias/", json=denuncia_valida_dados)
        
        assert response.status_code == 401
    
    def test_criar_denuncia_categoria_invalida(
        self,
        client: TestClient,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de criação de denúncia com categoria inválida"""
        dados = denuncia_valida_dados.copy()
        dados["categoria"] = "CATEGORIA_INEXISTENTE"
        
        response = client.post(
            "/api/denuncias/",
            json=dados,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_criar_denuncia_campos_obrigatorios(
        self,
        client: TestClient,
        usuario_autenticado: dict
    ):
        """Teste de criação de denúncia sem campos obrigatórios"""
        dados_incompletos = {
            "categoria": "POLUICAO"
            # Faltam outros campos obrigatórios
        }
        
        response = client.post(
            "/api/denuncias/",
            json=dados_incompletos,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 422


class TestListarDenuncias:
    """Testes de listagem de denúncias"""
    
    def test_listar_minhas_denuncias(
        self,
        client: TestClient,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de listagem das próprias denúncias"""
        # Criar uma denúncia
        client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        
        # Listar denúncias
        response = client.get(
            "/api/denuncias/",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["denunciante_id"] == usuario_autenticado["usuario"]["id"]
    
    def test_listar_denuncias_sem_autenticacao(self, client: TestClient):
        """Teste de listagem sem autenticação"""
        response = client.get("/api/denuncias/")
        
        assert response.status_code == 401


class TestBuscarDenuncia:
    """Testes de busca de denúncia específica"""
    
    def test_buscar_denuncia_propria(
        self,
        client: TestClient,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de busca de denúncia própria"""
        # Criar denúncia
        response_criar = client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        denuncia_id = response_criar.json()["id"]
        
        # Buscar denúncia
        response = client.get(
            f"/api/denuncias/{denuncia_id}",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == denuncia_id
    
    def test_buscar_denuncia_inexistente(
        self,
        client: TestClient,
        usuario_autenticado: dict
    ):
        """Teste de busca de denúncia inexistente"""
        response = client.get(
            "/api/denuncias/99999",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 404


class TestAtualizarDenuncia:
    """Testes de atualização de denúncia"""
    
    def test_atualizar_denuncia_propria(
        self,
        client: TestClient,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de atualização de denúncia própria"""
        # Criar denúncia
        response_criar = client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        denuncia_id = response_criar.json()["id"]
        
        # Atualizar denúncia
        dados_atualizacao = {
            "descricao": "Descrição atualizada"
        }
        response = client.patch(
            f"/api/denuncias/{denuncia_id}",
            json=dados_atualizacao,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["descricao"] == dados_atualizacao["descricao"]
    
    def test_atualizar_denuncia_outro_usuario(
        self,
        client: TestClient,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de tentativa de atualizar denúncia de outro usuário"""
        # Criar denúncia com primeiro usuário
        response_criar = client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        denuncia_id = response_criar.json()["id"]
        
        # Criar segundo usuário
        usuario2_dados = {
            "cpf": "98765432100",
            "nome": "Usuário 2",
            "email": "usuario2@exemplo.com",
            "senha": "Senha@Forte123"
        }
        client.post("/api/auth/cadastro", json=usuario2_dados)
        
        # Login com segundo usuário
        response_login = client.post(
            "/api/auth/login",
            json={
                "email": usuario2_dados["email"],
                "senha": usuario2_dados["senha"]
            }
        )
        token2 = response_login.json()["access_token"]
        
        # Tentar atualizar denúncia do primeiro usuário
        response = client.patch(
            f"/api/denuncias/{denuncia_id}",
            json={"descricao": "Tentativa de alteração"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 403


class TestDeletarDenuncia:
    """Testes de exclusão de denúncia"""
    
    def test_deletar_denuncia_propria(
        self,
        client: TestClient,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de exclusão de denúncia própria"""
        # Criar denúncia
        response_criar = client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        denuncia_id = response_criar.json()["id"]
        
        # Deletar denúncia
        response = client.delete(
            f"/api/denuncias/{denuncia_id}",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 204
        
        # Verificar que foi deletada
        response_buscar = client.get(
            f"/api/denuncias/{denuncia_id}",
            headers=usuario_autenticado["headers"]
        )
        assert response_buscar.status_code == 404


class TestAtualizarStatusDenuncia:
    """Testes de atualização de status de denúncia"""
    
    def test_atualizar_status_como_admin(
        self,
        client: TestClient,
        admin_autenticado: dict,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de atualização de status por administrador"""
        # Criar denúncia com usuário comum
        response_criar = client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        denuncia_id = response_criar.json()["id"]
        
        # Admin atualiza status
        response = client.patch(
            f"/api/denuncias/{denuncia_id}/status",
            json={"status": "EM_ANALISE"},
            headers=admin_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "EM_ANALISE"
    
    def test_atualizar_status_sem_permissao(
        self,
        client: TestClient,
        usuario_autenticado: dict,
        denuncia_valida_dados: dict
    ):
        """Teste de atualização de status sem permissão de admin"""
        # Criar denúncia
        response_criar = client.post(
            "/api/denuncias/",
            json=denuncia_valida_dados,
            headers=usuario_autenticado["headers"]
        )
        denuncia_id = response_criar.json()["id"]
        
        # Tentar atualizar status sem ser admin
        response = client.patch(
            f"/api/denuncias/{denuncia_id}/status",
            json={"status": "EM_ANALISE"},
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 403
