# Suite de Testes - Plataforma GeoBot

## 📁 Estrutura

```
tests/
├── __init__.py              # Módulo de testes
├── conftest.py              # Fixtures globais do pytest
├── integration/             # Testes de integração (com HTTP)
│   ├── __init__.py
│   ├── test_auth.py         # Testes de autenticação
│   └── test_denuncias.py    # Testes de denúncias
└── unit/                    # Testes unitários (lógica isolada)
    ├── __init__.py
    ├── test_denuncia_service.py  # Testes do service
    └── test_denuncia_dtos.py     # Testes dos DTOs
```

## 🎯 Tipos de Testes

### Testes de Integração (`tests/integration/`)
- **Objetivo:** Testar fluxos completos da API
- **Método:** Usa `TestClient` do FastAPI para simular requisições HTTP
- **Banco de Dados:** SQLite em memória (isolado por teste)
- **Quando usar:** Para validar endpoints, autenticação, autorização

**Exemplo:**
```python
def test_criar_denuncia(client, usuario_autenticado, denuncia_valida_dados):
    response = client.post(
        "/api/denuncias/",
        json=denuncia_valida_dados,
        headers=usuario_autenticado["headers"]
    )
    assert response.status_code == 201
```

### Testes Unitários (`tests/unit/`)
- **Objetivo:** Testar lógica de negócio isoladamente
- **Método:** Testa services, DTOs, repositories diretamente
- **Banco de Dados:** SQLite em memória (quando necessário)
- **Quando usar:** Para validar regras de negócio, validações, transformações

**Exemplo:**
```python
def test_criar_denuncia_usuario_inativo(db_session):
    service = DenunciaService(db_session)
    with pytest.raises(AutorizacaoError):
        service.criar_denuncia(dto, usuario_inativo_id)
```

## 🚀 Executando os Testes

### Todos os Testes
```bash
pytest
```

### Apenas Testes de Integração
```bash
pytest tests/integration/
```

### Apenas Testes Unitários
```bash
pytest tests/unit/
```

### Teste Específico
```bash
pytest tests/integration/test_auth.py::TestLogin::test_login_sucesso
```

### Com Coverage
```bash
pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### Com Marcadores
```bash
# Apenas testes de autenticação
pytest -m auth

# Apenas testes de denúncias
pytest -m denuncias

# Excluir testes lentos
pytest -m "not slow"
```

## 🔧 Fixtures Disponíveis (conftest.py)

### Fixtures de Banco de Dados
- **`engine`**: Engine SQLite em memória (escopo: session)
- **`db_session`**: Sessão de banco isolada (escopo: function)
- **`client`**: TestClient do FastAPI com DB injetado

### Fixtures de Dados
- **`usuario_teste_dados`**: Dicionário com dados de usuário válido
- **`usuario_admin_dados`**: Dicionário com dados de admin válido
- **`denuncia_valida_dados`**: Dicionário com dados de denúncia válida

### Fixtures de Autenticação
- **`usuario_autenticado`**: Usuário criado e autenticado
  - Retorna: `{"access_token": str, "usuario": dict, "headers": dict}`
- **`admin_autenticado`**: Admin criado e autenticado
  - Retorna: `{"access_token": str, "usuario": dict, "headers": dict}`

## 📝 Convenções

### Nomenclatura
- **Arquivos:** `test_<modulo>.py`
- **Classes:** `Test<Funcionalidade>`
- **Funções:** `test_<acao>_<contexto>`

**Exemplos:**
```python
# ✅ Bom
def test_criar_denuncia_usuario_ativo()
def test_login_credenciais_invalidas()
def test_atualizar_status_sem_permissao()

# ❌ Evitar
def test_denuncia()
def test1()
def teste_criar()
```

### Estrutura AAA (Arrange-Act-Assert)
```python
def test_exemplo(client, usuario_autenticado):
    # Arrange: Preparar dados
    payload = {"campo": "valor"}
    
    # Act: Executar ação
    response = client.post("/endpoint", json=payload)
    
    # Assert: Verificar resultado
    assert response.status_code == 200
    assert response.json()["campo"] == "valor"
```

### Parametrização
Para testar múltiplos casos:
```python
@pytest.mark.parametrize("cpf,esperado", [
    ("12345678901", True),
    ("123", False),
    ("abc", False),
])
def test_validar_cpf(cpf, esperado):
    resultado = validar_cpf(cpf)
    assert resultado == esperado
```

## 🎨 Marcadores (Markers)

Use markers para categorizar testes:

```python
@pytest.mark.integration
def test_endpoint():
    ...

@pytest.mark.unit
def test_service():
    ...

@pytest.mark.slow
def test_operacao_pesada():
    ...

@pytest.mark.auth
def test_login():
    ...
```

Executar:
```bash
pytest -m integration  # Apenas integração
pytest -m "unit and auth"  # Unit E auth
pytest -m "not slow"  # Excluir lentos
```

## 🐛 Debugging

### Modo Verboso
```bash
pytest -vv
```

### Parar no Primeiro Erro
```bash
pytest -x
```

### Executar Último Teste que Falhou
```bash
pytest --lf
```

### Pdb (Python Debugger)
```python
def test_debug():
    import pdb; pdb.set_trace()
    # Código aqui
```

Ou adicionar `--pdb` ao pytest:
```bash
pytest --pdb
```

## 📊 Coverage

### Gerar Relatório de Coverage
```bash
# Terminal
pytest --cov=src --cov-report=term-missing

# HTML
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML (para CI/CD)
pytest --cov=src --cov-report=xml
```

### Meta de Coverage
- **Mínimo aceitável:** 70%
- **Recomendado:** 80%
- **Excelente:** 90%+

## 🔄 CI/CD

Exemplo de configuração para GitHub Actions:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## 📚 Boas Práticas

### ✅ Fazer
- ✅ Testar casos de sucesso E de erro
- ✅ Usar nomes descritivos de testes
- ✅ Manter testes independentes (não dependem de ordem)
- ✅ Usar fixtures para reutilizar código
- ✅ Testar comportamento, não implementação
- ✅ Manter testes rápidos
- ✅ Um assert por conceito

### ❌ Evitar
- ❌ Testes que dependem de ordem de execução
- ❌ Testes que dependem de dados externos (API, arquivos)
- ❌ Testes muito longos (dividir em múltiplos testes)
- ❌ Testar implementação interna (teste a interface)
- ❌ Duplicar código de teste (use fixtures)

## 🎓 Exemplos Completos

### Teste de Integração Completo
```python
def test_fluxo_completo_denuncia(client, usuario_autenticado):
    # Criar denúncia
    response = client.post(
        "/api/denuncias/",
        json={"categoria": "POLUICAO", "descricao": "Teste"},
        headers=usuario_autenticado["headers"]
    )
    assert response.status_code == 201
    denuncia_id = response.json()["id"]
    
    # Buscar denúncia
    response = client.get(
        f"/api/denuncias/{denuncia_id}",
        headers=usuario_autenticado["headers"]
    )
    assert response.status_code == 200
    
    # Atualizar denúncia
    response = client.patch(
        f"/api/denuncias/{denuncia_id}",
        json={"descricao": "Atualizado"},
        headers=usuario_autenticado["headers"]
    )
    assert response.status_code == 200
    
    # Deletar denúncia
    response = client.delete(
        f"/api/denuncias/{denuncia_id}",
        headers=usuario_autenticado["headers"]
    )
    assert response.status_code == 204
```

### Teste Unitário Completo
```python
def test_service_com_autorizacao(db_session):
    # Arrange
    service = DenunciaService(db_session)
    usuario1 = criar_usuario(db_session, "usuario1@email.com")
    usuario2 = criar_usuario(db_session, "usuario2@email.com")
    denuncia = criar_denuncia(db_session, usuario1.id)
    
    # Act & Assert
    with pytest.raises(AutorizacaoError):
        service.deletar_denuncia(denuncia.id, usuario2.id)
```

## 📞 Suporte

Para dúvidas sobre testes:
1. Consultar documentação do pytest: https://docs.pytest.org/
2. Ver exemplos nos testes existentes
3. Consultar fixtures em `conftest.py`

---

**Última atualização:** 1 de novembro de 2025
**Status:** ✅ Suite de testes estruturada e funcional
