"""
Testes de integração do sistema de autenticação.

Este módulo testa os endpoints de autenticação usando TestClient do FastAPI.
"""
import pytest
from fastapi.testclient import TestClient


class TestCadastro:
    """Testes de cadastro de usuário"""
    
    def test_cadastro_sucesso(self, client: TestClient, usuario_teste_dados: dict):
        """Teste de cadastro com dados válidos"""
        response = client.post("/api/auth/cadastro", json=usuario_teste_dados)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == usuario_teste_dados["email"]
        assert data["nome"] == usuario_teste_dados["nome"]
        assert data["cpf"] == usuario_teste_dados["cpf"]
        assert "senha" not in data  # Senha não deve ser retornada
    
    def test_cadastro_senha_fraca(self, client: TestClient):
        """Teste de cadastro com senha fraca"""
        dados = {
            "cpf": "98765432100",
            "nome": "Teste Senha Fraca",
            "email": "senha_fraca@exemplo.com",
            "senha": "123"  # Senha muito fraca
        }
        response = client.post("/api/auth/cadastro", json=dados)
        
        assert response.status_code == 400
        assert "senha" in response.json()["detail"].lower()
    
    def test_cadastro_email_invalido(self, client: TestClient):
        """Teste de cadastro com email inválido"""
        dados = {
            "cpf": "98765432100",
            "nome": "Teste Email",
            "email": "email_invalido",
            "senha": "Senha@Forte123"
        }
        response = client.post("/api/auth/cadastro", json=dados)
        
        assert response.status_code == 422  # Validation error do Pydantic
    
    def test_cadastro_cpf_invalido(self, client: TestClient):
        """Teste de cadastro com CPF inválido"""
        dados = {
            "cpf": "123",  # CPF muito curto
            "nome": "Teste CPF",
            "email": "cpf_invalido@exemplo.com",
            "senha": "Senha@Forte123"
        }
        response = client.post("/api/auth/cadastro", json=dados)
        
        assert response.status_code == 400
    
    def test_cadastro_email_duplicado(self, client: TestClient, usuario_teste_dados: dict):
        """Teste de cadastro com email já existente"""
        # Primeiro cadastro
        response = client.post("/api/auth/cadastro", json=usuario_teste_dados)
        assert response.status_code == 201
        
        # Segundo cadastro com mesmo email
        dados_duplicado = usuario_teste_dados.copy()
        dados_duplicado["cpf"] = "98765432100"  # CPF diferente
        response = client.post("/api/auth/cadastro", json=dados_duplicado)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()


class TestLogin:
    """Testes de login"""
    
    def test_login_sucesso(self, client: TestClient, usuario_teste_dados: dict):
        """Teste de login com credenciais válidas"""
        # Cadastrar usuário primeiro
        client.post("/api/auth/cadastro", json=usuario_teste_dados)
        
        # Fazer login
        response = client.post(
            "/api/auth/login",
            json={
                "email": usuario_teste_dados["email"],
                "senha": usuario_teste_dados["senha"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "usuario" in data
        assert data["usuario"]["email"] == usuario_teste_dados["email"]
    
    def test_login_email_invalido(self, client: TestClient):
        """Teste de login com email inexistente"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "naoexiste@exemplo.com",
                "senha": "SenhaQualquer123"
            }
        )
        
        assert response.status_code == 401
        assert "credenciais" in response.json()["detail"].lower()
    
    def test_login_senha_incorreta(self, client: TestClient, usuario_teste_dados: dict):
        """Teste de login com senha incorreta"""
        # Cadastrar usuário
        client.post("/api/auth/cadastro", json=usuario_teste_dados)
        
        # Tentar login com senha errada
        response = client.post(
            "/api/auth/login",
            json={
                "email": usuario_teste_dados["email"],
                "senha": "SenhaErrada123"
            }
        )
        
        assert response.status_code == 401
        assert "credenciais" in response.json()["detail"].lower()
    
    def test_login_usuario_inativo(self, client: TestClient, usuario_teste_dados: dict, db_session):
        """Teste de login com usuário inativo"""
        from src.geobot_plataforma_backend.domain.entity import Usuario
        
        # Cadastrar usuário
        response = client.post("/api/auth/cadastro", json=usuario_teste_dados)
        usuario_id = response.json()["id"]
        
        # Desativar usuário
        usuario = db_session.query(Usuario).filter_by(id=usuario_id).first()
        usuario.ativo = False
        db_session.commit()
        
        # Tentar login
        response = client.post(
            "/api/auth/login",
            json={
                "email": usuario_teste_dados["email"],
                "senha": usuario_teste_dados["senha"]
            }
        )
        
        assert response.status_code == 401
        assert "inativo" in response.json()["detail"].lower()


class TestAutenticacao:
    """Testes de endpoints autenticados"""
    
    def test_obter_usuario_autenticado(self, client: TestClient, usuario_autenticado: dict):
        """Teste de obtenção de dados do usuário autenticado"""
        response = client.get(
            "/api/auth/me",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == usuario_autenticado["usuario"]["email"]
        assert "senha" not in data
    
    def test_acesso_sem_token(self, client: TestClient):
        """Teste de acesso a rota protegida sem token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_acesso_token_invalido(self, client: TestClient):
        """Teste de acesso com token inválido"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer token_invalido_123"}
        )
        
        assert response.status_code == 401
    
    def test_validar_token_valido(self, client: TestClient, usuario_autenticado: dict):
        """Teste de validação de token válido"""
        response = client.get(
            "/api/auth/validar-token",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valido"] is True
    
    def test_validar_token_invalido(self, client: TestClient):
        """Teste de validação de token inválido"""
        response = client.get(
            "/api/auth/validar-token",
            headers={"Authorization": "Bearer token_invalido"}
        )
        
        assert response.status_code == 401


class TestLogout:
    """Testes de logout"""
    
    def test_logout_sucesso(self, client: TestClient, usuario_autenticado: dict):
        """Teste de logout com sucesso"""
        response = client.post(
            "/api/auth/logout",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "mensagem" in data
