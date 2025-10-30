#!/usr/bin/env python3
"""
CLI para gerenciamento de migrations do banco de dados
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.geobot_plataforma_backend.core.migrations import (
    run_migrations,
    create_migration,
    downgrade_migration,
    show_current_revision,
    show_migration_history,
    check_pending_migrations
)


def main():
    """Função principal do CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🗄️  Gerenciador de Migrations do Geobot Plataforma",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python manage_db.py upgrade                           # Executa migrations pendentes
  python manage_db.py create -m "adicionar_campo_x"    # Cria nova migration
  python manage_db.py downgrade                         # Desfaz última migration
  python manage_db.py current                           # Mostra versão atual
  python manage_db.py history                           # Mostra histórico
  python manage_db.py check                             # Verifica migrations pendentes
        """
    )
    
    parser.add_argument(
        "action",
        choices=["upgrade", "downgrade", "create", "current", "history", "check"],
        help="Ação a ser executada"
    )
    
    parser.add_argument(
        "-m", "--message",
        help="Mensagem da migration (obrigatório para 'create')"
    )
    
    parser.add_argument(
        "-r", "--revision",
        default="-1",
        help="Revisão alvo para downgrade (padrão: -1 = última)"
    )
    
    parser.add_argument(
        "--no-autogenerate",
        action="store_true",
        help="Não usar autogenerate ao criar migration (cria migration vazia)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.action == "upgrade":
            print("\n🚀 Executando migrations...\n")
            run_migrations()
            
        elif args.action == "downgrade":
            print(f"\n⏪ Desfazendo migration para: {args.revision}\n")
            downgrade_migration(args.revision)
            
        elif args.action == "create":
            if not args.message:
                print("❌ Erro: --message é obrigatório para criar uma migration")
                parser.print_help()
                sys.exit(1)
            print(f"\n📝 Criando migration: {args.message}\n")
            create_migration(args.message, not args.no_autogenerate)
            
        elif args.action == "current":
            print("\n📍 Revisão atual do banco de dados:\n")
            show_current_revision()
            
        elif args.action == "history":
            print("\n📚 Histórico de migrations:\n")
            show_migration_history()
            
        elif args.action == "check":
            print("\n🔍 Verificando migrations pendentes...\n")
            has_pending, message = check_pending_migrations()
            print(f"{'⚠️ ' if has_pending else '✅ '}{message}\n")
            sys.exit(1 if has_pending else 0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

