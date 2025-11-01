"""
Configuração de fixtures do pytest para toda a suite de testes
"""
import sys
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.geobot_plataforma_backend.app_fastapi import app
from src.geobot_plataforma_backend.core.database import Base, get_db
from src.geobot_plataforma_backend.domain.entity import Usuario, Grupo, Role


# =============================================================================
# FIXTURES DE BANCO DE DADOS
# =============================================================================

@pytest.fixture(scope="session")
def engine():
    """
    Cria um engine SQLite em memória para testes.
    Escopo: session - criado uma vez para toda a sessão de testes.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """
    Cria uma sessão de banco de dados isolada para cada teste.
    Escopo: function - cada teste recebe uma sessão limpa.
    
    Ao final do teste, faz rollback de todas as mudanças.
    """
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """
    Cria um TestClient do FastAPI com injeção de dependência do banco de testes.
    
    Override da dependência get_db para usar o banco de testes em memória.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# =============================================================================
# FIXTURES DE DADOS DE TESTE
# =============================================================================

@pytest.fixture
def usuario_teste_dados() -> dict:
    """
    Dados de um usuário válido para testes.
    """
    return {
        "cpf": "12345678901",
        "nome": "Usuário Teste",
        "email": "usuario_teste@exemplo.com",
        "senha": "Senha@Forte123"
    }


@pytest.fixture
def usuario_admin_dados() -> dict:
    """
    Dados de um usuário administrador para testes.
    """
    return {
        "cpf": "98765432100",
        "nome": "Admin Teste",
        "email": "admin_teste@exemplo.com",
        "senha": "Admin@Forte123"
    }


@pytest.fixture
def denuncia_valida_dados() -> dict:
    """
    Dados de uma denúncia válida para testes.
    """
    return {
        "categoria": "POLUICAO",
        "descricao": "Descarte irregular de lixo",
        "logradouro": "Rua Teste, 123",
        "bairro": "Centro",
        "cidade": "Cidade Teste",
        "estado": "SP",
        "cep": "12345678",
        "latitude": -23.5505,
        "longitude": -46.6333
    }


# =============================================================================
# FIXTURES DE AUTENTICAÇÃO
# =============================================================================

@pytest.fixture
def usuario_autenticado(client: TestClient, usuario_teste_dados: dict) -> dict:
    """
    Cria um usuário, faz login e retorna os dados de autenticação.
    
    Returns:
        dict: {
            "access_token": str,
            "usuario": dict,
            "headers": dict
        }
    """
    # Cadastrar usuário
    response = client.post("/api/auth/cadastro", json=usuario_teste_dados)
    assert response.status_code == 201
    usuario = response.json()
    
    # Fazer login
    response = client.post(
        "/api/auth/login",
        json={
            "email": usuario_teste_dados["email"],
            "senha": usuario_teste_dados["senha"]
        }
    )
    assert response.status_code == 200
    auth_data = response.json()
    
    return {
        "access_token": auth_data["access_token"],
        "usuario": auth_data["usuario"],
        "headers": {"Authorization": f"Bearer {auth_data['access_token']}"}
    }


@pytest.fixture
def admin_autenticado(client: TestClient, usuario_admin_dados: dict, db_session: Session) -> dict:
    """
    Cria um usuário administrador, faz login e retorna os dados de autenticação.
    
    Returns:
        dict: {
            "access_token": str,
            "usuario": dict,
            "headers": dict
        }
    """
    # Cadastrar usuário
    response = client.post("/api/auth/cadastro", json=usuario_admin_dados)
    assert response.status_code == 201
    usuario_data = response.json()
    
    # Buscar usuário no banco e adicionar ao grupo admin
    usuario = db_session.query(Usuario).filter_by(id=usuario_data["id"]).first()
    
    # Criar role e grupo admin se não existir
    role_admin = db_session.query(Role).filter_by(nome="admin").first()
    if not role_admin:
        role_admin = Role(nome="admin", descricao="Administrador")
        db_session.add(role_admin)
        db_session.flush()
    
    grupo_admin = db_session.query(Grupo).filter_by(nome="Administradores").first()
    if not grupo_admin:
        grupo_admin = Grupo(nome="Administradores", descricao="Grupo de administradores")
        grupo_admin.roles.append(role_admin)
        db_session.add(grupo_admin)
        db_session.flush()
    
    # Adicionar usuário ao grupo
    if usuario and grupo_admin not in usuario.grupos:
        usuario.grupos.append(grupo_admin)
        db_session.commit()
    
    # Fazer login
    response = client.post(
        "/api/auth/login",
        json={
            "email": usuario_admin_dados["email"],
            "senha": usuario_admin_dados["senha"]
        }
    )
    assert response.status_code == 200
    auth_data = response.json()
    
    return {
        "access_token": auth_data["access_token"],
        "usuario": auth_data["usuario"],
        "headers": {"Authorization": f"Bearer {auth_data['access_token']}"}
    }


# =============================================================================
# FIXTURES DE LIMPEZA
# =============================================================================

@pytest.fixture(autouse=True)
def limpar_overrides():
    """
    Limpa os overrides de dependências após cada teste.
    autouse=True: executado automaticamente para todos os testes.
    """
    yield
    app.dependency_overrides.clear()
