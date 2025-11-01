#!/bin/bash
# Script de comandos úteis para o projeto Geobot Plataforma Backend

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Comandos Úteis - Geobot Plataforma Backend      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📦 SETUP INICIAL:${NC}"
echo "  cp .env.example .env                    # Copiar template de variáveis"
echo "  createdb geobot_db                      # Criar banco de dados"
echo "  python test_setup.py                    # Testar configuração"
echo "  python manage_db.py upgrade             # Executar migrations"
echo ""

echo -e "${YELLOW}🚀 APLICAÇÃO:${NC}"
echo "  python app.py                           # Iniciar aplicação FastAPI"
echo "  uvicorn src.geobot_plataforma_backend.app_fastapi:app --reload"
echo ""

echo -e "${YELLOW}🗄️ MIGRATIONS:${NC}"
echo "  python manage_db.py check               # Verificar migrations pendentes"
echo "  python manage_db.py upgrade             # Executar migrations"
echo "  python manage_db.py current             # Ver versão atual"
echo "  python manage_db.py history             # Ver histórico"
echo "  python manage_db.py create -m 'msg'     # Criar nova migration"
echo "  python manage_db.py downgrade           # Desfazer última migration"
echo ""

echo -e "${YELLOW}🧪 TESTES:${NC}"
echo "  python test_setup.py                    # Testar configuração completa"
echo "  pytest                                  # Executar testes (quando disponível)"
echo ""

echo -e "${YELLOW}🗄️ BANCO DE DADOS:${NC}"
echo "  # PostgreSQL"
echo "  psql -U postgres -d geobot_db           # Conectar ao banco"
echo "  pg_dump geobot_db > backup.sql          # Fazer backup"
echo "  psql geobot_db < backup.sql             # Restaurar backup"
echo ""
echo "  # Ver tabelas e dados"
echo "  psql -U postgres -d geobot_db -c '\\dt'  # Listar tabelas"
echo "  psql -U postgres -d geobot_db -c 'SELECT * FROM grupos;'"
echo "  psql -U postgres -d geobot_db -c 'SELECT * FROM roles;'"
echo ""

echo -e "${YELLOW}🐳 DOCKER:${NC}"
echo "  docker-compose up -d                    # Iniciar containers"
echo "  docker-compose down                     # Parar containers"
echo "  docker-compose logs -f                  # Ver logs"
echo "  docker-compose exec app python manage_db.py upgrade"
echo ""

echo -e "${YELLOW}🔧 DESENVOLVIMENTO:${NC}"
echo "  # Criar nova migration após mudar models"
echo "  python manage_db.py create -m 'adicionar_campo_x'"
echo ""
echo "  # Verificar status"
echo "  python -c 'from src.geobot_plataforma_backend.core.database import check_db_connection; print(check_db_connection())'"
echo ""
echo "  # Listar tabelas via Python"
echo "  python -c 'from src.geobot_plataforma_backend.core.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())'"
echo ""

echo -e "${YELLOW}📚 DOCUMENTAÇÃO:${NC}"
echo "  cat SETUP_SUMMARY.md                    # Resumo da configuração"
echo "  cat MIGRATIONS_README.md                # Guia de migrations"
echo "  cat README.md                           # README principal"
echo ""

echo -e "${YELLOW}🆘 TROUBLESHOOTING:${NC}"
echo "  # Resetar banco (CUIDADO: apaga tudo!)"
echo "  psql -U postgres -c 'DROP DATABASE geobot_db;'"
echo "  psql -U postgres -c 'CREATE DATABASE geobot_db;'"
echo "  python manage_db.py upgrade"
echo ""
echo "  # Verificar configuração"
echo "  python -c 'from src.geobot_plataforma_backend.core.config import settings; print(settings.as_dict())'"
echo ""
echo "  # Forçar migration para uma versão"
echo "  alembic stamp head                      # Marcar como atualizado"
echo "  alembic stamp base                      # Marcar como vazio"
echo ""

echo -e "${GREEN}✨ Para mais detalhes, consulte a documentação em:${NC}"
echo "   - SETUP_SUMMARY.md"
echo "   - MIGRATIONS_README.md"
echo "   - README.md"
echo ""

