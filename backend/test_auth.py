#!/usr/bin/env python
"""
Script de teste para o sistema de autenticação
Execute: python test_auth.py
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER = {
    "cpf": "12345678901",
    "nome": "Usuário Teste",
    "email": f"teste_{datetime.now().timestamp()}@exemplo.com",
    "senha": "Senha@Forte123"
}

def print_response(title, response):
    """Imprime a resposta formatada"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_health():
    """Testa se o servidor está rodando"""
    print("🔍 Testando conexão com o servidor...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response("Health Check", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao conectar com o servidor: {e}")
        print("⚠️  Certifique-se de que o servidor está rodando: python app.py")
        return False

def test_cadastro():
    """Testa o cadastro de usuário"""
    print("📝 Testando cadastro de usuário...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/cadastro",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        print_response("Cadastro de Usuário", response)
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Erro no cadastro: {e}")
        return False

def test_login():
    """Testa o login de usuário"""
    print("🔐 Testando login de usuário...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_USER["email"],
                "senha": TEST_USER["senha"]
            },
            headers={"Content-Type": "application/json"}
        )
        print_response("Login de Usuário", response)
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def test_me(token):
    """Testa a obtenção de dados do usuário autenticado"""
    print("👤 Testando obtenção de dados do usuário...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        print_response("Dados do Usuário", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao obter dados: {e}")
        return False

def test_validar_token(token):
    """Testa a validação do token"""
    print("✅ Testando validação de token...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/validar-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        print_response("Validação de Token", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def test_logout(token):
    """Testa o logout"""
    print("🚪 Testando logout...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        print_response("Logout", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro no logout: {e}")
        return False

def test_senha_fraca():
    """Testa validação de senha fraca"""
    print("🔒 Testando validação de senha fraca...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/cadastro",
            json={
                "cpf": "98765432100",
                "nome": "Teste Senha Fraca",
                "email": f"fraca_{datetime.now().timestamp()}@exemplo.com",
                "senha": "123"  # Senha fraca
            },
            headers={"Content-Type": "application/json"}
        )
        print_response("Senha Fraca (deve falhar)", response)
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_login_invalido():
    """Testa login com credenciais inválidas"""
    print("❌ Testando login com credenciais inválidas...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "naoexiste@exemplo.com",
                "senha": "SenhaErrada123"
            },
            headers={"Content-Type": "application/json"}
        )
        print_response("Login Inválido (deve falhar)", response)
        return response.status_code == 401
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_acesso_sem_token():
    """Testa acesso a rota protegida sem token"""
    print("🚫 Testando acesso sem token...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me")
        print_response("Acesso sem Token (deve falhar)", response)
        return response.status_code == 401
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 INICIANDO TESTES DO SISTEMA DE AUTENTICAÇÃO")
    print("="*60)
    
    resultados = []
    
    # Teste 1: Health Check
    resultados.append(("Health Check", test_health()))
    
    if not resultados[0][1]:
        print("\n❌ Servidor não está respondendo. Encerrando testes.")
        return
    
    # Teste 2: Cadastro
    resultados.append(("Cadastro", test_cadastro()))
    
    # Teste 3: Login
    token = test_login()
    resultados.append(("Login", token is not None))
    
    if token:
        # Teste 4: Obter dados do usuário
        resultados.append(("Obter Dados", test_me(token)))
        
        # Teste 5: Validar token
        resultados.append(("Validar Token", test_validar_token(token)))
        
        # Teste 6: Logout
        resultados.append(("Logout", test_logout(token)))
    
    # Testes de validação
    resultados.append(("Senha Fraca", test_senha_fraca()))
    resultados.append(("Login Inválido", test_login_invalido()))
    resultados.append(("Acesso sem Token", test_acesso_sem_token()))
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60)
    
    total = len(resultados)
    sucesso = sum(1 for _, passou in resultados if passou)
    
    for nome, passou in resultados:
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{status} - {nome}")
    
    print(f"\n{'='*60}")
    print(f"Total: {sucesso}/{total} testes passaram")
    print(f"{'='*60}\n")
    
    if sucesso == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verifique os logs acima.")

if __name__ == "__main__":
    main()

