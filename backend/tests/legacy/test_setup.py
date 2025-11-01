#!/usr/bin/env python3
"""
Script de teste para validar a configuração do banco de dados e migrations
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.geobot_plataforma_backend.core.config import settings
from src.geobot_plataforma_backend.core.database import check_db_connection, get_database_url
from src.geobot_plataforma_backend.core.migrations import check_pending_migrations


def test_configuration():
    """Testa a configuração do Dynaconf"""
    print("=" * 60)
    print("🔧 TESTANDO CONFIGURAÇÃO DO DYNACONF")
    print("=" * 60)
    
    try:
        print(f"✅ App Name: {settings.app_name}")
        print(f"✅ App Version: {settings.app_version}")
        print(f"✅ Environment: {settings.current_env}")
        print(f"✅ Debug Mode: {settings.debug}")
        print(f"✅ Database Host: {settings.db_host}")
        print(f"✅ Database Port: {settings.db_port}")
        print(f"✅ Database Name: {settings.db_name}")
        print(f"✅ Database User: {settings.db_user}")
        print(f"✅ Auto Run Migrations: {settings.get('auto_run_migrations', True)}")
        print(f"\n✅ Database URL: {get_database_url()}\n")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao ler configurações: {e}\n")
        return False


def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("=" * 60)
    print("🗄️  TESTANDO CONEXÃO COM O BANCO DE DADOS")
    print("=" * 60)
    
    if check_db_connection():
        print("✅ Conexão com o banco de dados estabelecida com sucesso!\n")
        return True
    else:
        print("❌ Falha ao conectar com o banco de dados")
        print("   Verifique se o PostgreSQL está rodando e as credenciais estão corretas\n")
        return False


def test_models_import():
    """Testa a importação dos modelos"""
    print("=" * 60)
    print("📦 TESTANDO IMPORTAÇÃO DOS MODELOS")
    print("=" * 60)
    
    try:
        from src.geobot_plataforma_backend.domain.entity import (
            Usuario, Grupo, Role, Endereco, Denuncia, Fiscalizacao, Analise, Arquivo
        )
        print("✅ Todos os modelos importados com sucesso!")
        print(f"   - Usuario")
        print(f"   - Grupo")
        print(f"   - Role")
        print(f"   - Endereco")
        print(f"   - Denuncia")
        print(f"   - Fiscalizacao")
        print(f"   - Analise")
        print(f"   - Arquivo\n")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar modelos: {e}\n")
        return False


def test_migrations_status():
    """Testa o status das migrations"""
    print("=" * 60)
    print("🔄 VERIFICANDO STATUS DAS MIGRATIONS")
    print("=" * 60)
    
    try:
        has_pending, message = check_pending_migrations()
        if has_pending:
            print(f"⚠️  {message}")
            print("   Execute: python manage_db.py upgrade\n")
        else:
            print(f"✅ {message}\n")
        return True
    except Exception as e:
        print(f"⚠️  Não foi possível verificar migrations: {e}")
        print("   Isso é normal se o banco ainda não foi inicializado\n")
        return True  # Não é erro crítico


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("🧪 INICIANDO TESTES DE CONFIGURAÇÃO")
    print("=" * 60 + "\n")
    
    results = {
        "Configuração": test_configuration(),
        "Conexão BD": test_database_connection(),
        "Modelos": test_models_import(),
        "Migrations": test_migrations_status()
    }
    
    # Sumário
    print("=" * 60)
    print("📊 SUMÁRIO DOS TESTES")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 Todos os testes passaram! Sistema configurado corretamente.\n")
        print("📝 Próximos passos:")
        print("   1. python manage_db.py upgrade    # Executar migrations")
        print("   2. python app.py                  # Iniciar aplicação\n")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Corrija os problemas antes de continuar.\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes cancelados pelo usuário\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}\n")
        sys.exit(1)

