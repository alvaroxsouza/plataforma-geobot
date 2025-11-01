#!/bin/bash
# COMANDOS ÚTEIS - TESTES
# Execute: source COMANDOS_TESTES.sh

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}🧪 COMANDOS ÚTEIS - TESTES${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# ============================================================================
# INSTALAÇÃO
# ============================================================================

alias instalar-testes='echo -e "${YELLOW}Instalando dependências de teste...${NC}" && pip install pytest pytest-cov requests'

# ============================================================================
# EXECUÇÃO DE TESTES
# ============================================================================

# Executar todos os testes
alias testar='pytest'
alias testes='pytest'

# Testes com modo verboso
alias testar-v='pytest -v'
alias testar-vv='pytest -vv'

# Testes de integração
alias testar-integracao='pytest tests/integration/'
alias testar-int='pytest tests/integration/'

# Testes unitários
alias testar-unit='pytest tests/unit/'
alias testar-unitarios='pytest tests/unit/'

# Testes específicos
alias testar-auth='pytest tests/integration/test_auth.py'
alias testar-denuncias='pytest tests/integration/test_denuncias.py'
alias testar-service='pytest tests/unit/test_denuncia_service.py'
alias testar-dtos='pytest tests/unit/test_denuncia_dtos.py'

# Testes com markers
alias testar-integracao-marker='pytest -m integration'
alias testar-unit-marker='pytest -m unit'
alias testar-auth-marker='pytest -m auth'
alias testar-denuncias-marker='pytest -m denuncias'

# ============================================================================
# COVERAGE
# ============================================================================

# Coverage básico
alias testar-cov='pytest --cov=src'

# Coverage com relatório HTML
alias testar-cov-html='pytest --cov=src --cov-report=html && echo -e "${GREEN}Abrir: firefox htmlcov/index.html${NC}"'

# Coverage com relatório detalhado no terminal
alias testar-cov-term='pytest --cov=src --cov-report=term-missing'

# Coverage completo (HTML + Terminal)
alias testar-cov-completo='pytest --cov=src --cov-report=html --cov-report=term-missing'

# Abrir relatório de coverage
alias ver-cov='xdg-open htmlcov/index.html 2>/dev/null || open htmlcov/index.html 2>/dev/null || firefox htmlcov/index.html 2>/dev/null'

# ============================================================================
# DEBUGGING
# ============================================================================

# Modo debug (para no primeiro erro)
alias testar-debug='pytest -x'

# Debug com pdb
alias testar-pdb='pytest --pdb'

# Executar último teste que falhou
alias testar-ultimo='pytest --lf'

# Executar testes que falharam e depois todos
alias testar-falhos='pytest --ff'

# ============================================================================
# FILTROS E SELEÇÃO
# ============================================================================

# Executar teste específico por nome
testar-nome() {
    pytest -k "$1"
}

# Executar teste específico por caminho
testar-arquivo() {
    pytest "$1"
}

# Executar classe específica
testar-classe() {
    pytest "$1"
}

# ============================================================================
# PERFORMANCE
# ============================================================================

# Mostrar os 10 testes mais lentos
alias testar-lentos='pytest --durations=10'

# Executar testes em paralelo (requer pytest-xdist)
alias testar-paralelo='pytest -n auto'

# ============================================================================
# LIMPEZA
# ============================================================================

# Limpar cache do pytest
alias limpar-pytest='rm -rf .pytest_cache'

# Limpar coverage
alias limpar-cov='rm -rf .coverage htmlcov/'

# Limpar __pycache__
alias limpar-pycache='find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null'

# Limpar tudo
alias limpar-testes='limpar-pytest && limpar-cov && limpar-pycache && echo -e "${GREEN}✅ Limpeza concluída${NC}"'

# ============================================================================
# SCRIPTS LEGADOS
# ============================================================================

# Executar script de teste HTTP manual
alias testar-http='python tests/legacy/test_auth.py'

# Executar script de validação de setup
alias testar-setup='python tests/legacy/test_setup.py'

# ============================================================================
# DOCUMENTAÇÃO
# ============================================================================

# Ver documentação dos testes
alias doc-testes='cat tests/README.md | less'

# Ver fixtures disponíveis
alias ver-fixtures='pytest --fixtures'

# Ver markers disponíveis
alias ver-markers='pytest --markers'

# ============================================================================
# CI/CD
# ============================================================================

# Simular pipeline de CI/CD
alias ci-local='limpar-testes && pytest --cov=src --cov-report=xml --cov-report=term'

# ============================================================================
# FUNÇÕES ÚTEIS
# ============================================================================

# Executar testes e abrir coverage se passar
testar-completo() {
    echo -e "${YELLOW}Executando testes com coverage...${NC}"
    pytest --cov=src --cov-report=html --cov-report=term-missing
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Todos os testes passaram!${NC}"
        echo -e "${BLUE}Abrindo relatório de coverage...${NC}"
        ver-cov
    else
        echo -e "${YELLOW}⚠️  Alguns testes falharam${NC}"
    fi
}

# Assistir mudanças e executar testes (requer pytest-watch)
testar-watch() {
    echo -e "${BLUE}Assistindo mudanças nos arquivos...${NC}"
    pytest-watch -c
}

# ============================================================================
# MENSAGEM DE AJUDA
# ============================================================================

ajuda-testes() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${GREEN}Comandos Disponíveis${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "${YELLOW}Instalação:${NC}"
    echo "  instalar-testes         - Instalar pytest, pytest-cov, requests"
    echo ""
    echo -e "${YELLOW}Execução:${NC}"
    echo "  testar                  - Executar todos os testes"
    echo "  testar-v                - Executar com modo verboso"
    echo "  testar-integracao       - Apenas testes de integração"
    echo "  testar-unit             - Apenas testes unitários"
    echo "  testar-auth             - Apenas testes de autenticação"
    echo "  testar-denuncias        - Apenas testes de denúncias"
    echo ""
    echo -e "${YELLOW}Coverage:${NC}"
    echo "  testar-cov              - Executar com coverage"
    echo "  testar-cov-html         - Coverage com relatório HTML"
    echo "  testar-cov-term         - Coverage com detalhes no terminal"
    echo "  ver-cov                 - Abrir relatório de coverage"
    echo ""
    echo -e "${YELLOW}Debugging:${NC}"
    echo "  testar-debug            - Parar no primeiro erro"
    echo "  testar-pdb              - Entrar no debugger em falhas"
    echo "  testar-ultimo           - Executar último teste que falhou"
    echo "  testar-lentos           - Mostrar testes mais lentos"
    echo ""
    echo -e "${YELLOW}Limpeza:${NC}"
    echo "  limpar-pytest           - Limpar cache do pytest"
    echo "  limpar-cov              - Limpar coverage"
    echo "  limpar-pycache          - Limpar __pycache__"
    echo "  limpar-testes           - Limpar tudo"
    echo ""
    echo -e "${YELLOW}Funções:${NC}"
    echo "  testar-completo         - Executar testes e abrir coverage"
    echo "  testar-nome <nome>      - Executar teste por nome"
    echo ""
    echo -e "${YELLOW}Documentação:${NC}"
    echo "  doc-testes              - Ver documentação completa"
    echo "  ver-fixtures            - Ver fixtures disponíveis"
    echo "  ver-markers             - Ver markers disponíveis"
    echo ""
}

# Mostrar ajuda
ajuda-testes

echo ""
echo -e "${GREEN}Para ver esta mensagem novamente: ${YELLOW}ajuda-testes${NC}"
echo -e "${GREEN}Para carregar no terminal: ${YELLOW}source COMANDOS_TESTES.sh${NC}"
echo ""
