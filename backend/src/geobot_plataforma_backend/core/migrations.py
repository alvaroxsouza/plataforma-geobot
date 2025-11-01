"""
Utilitário para gerenciamento de migrations do Alembic
"""
import sys
from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from src.geobot_plataforma_backend.core.database import engine


def get_alembic_config():
    """Retorna a configuração do Alembic"""
    # Encontrar o diretório raiz do projeto
    base_path = Path(__file__).parent.parent.parent.parent
    alembic_ini_path = base_path / "alembic.ini"
    
    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"Arquivo alembic.ini não encontrado em: {alembic_ini_path}")
    
    alembic_cfg = Config(str(alembic_ini_path))
    return alembic_cfg


def get_current_revision():
    """Retorna a revisão atual do banco de dados"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        # Tabela alembic_version não existe ainda
        return None


def get_head_revision():
    """Retorna a última revisão disponível"""
    alembic_cfg = get_alembic_config()
    script = ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def check_pending_migrations():
    """Verifica se existem migrations pendentes"""
    current = get_current_revision()
    head = get_head_revision()
    
    if current is None:
        return True, "Banco de dados não inicializado"
    
    if current != head:
        return True, f"Migration pendente: {current} -> {head}"
    
    return False, "Banco de dados atualizado"


def run_migrations():
    """Executa as migrations pendentes"""
    try:
        alembic_cfg = get_alembic_config()
        
        print("🔄 Verificando migrations...")
        has_pending, message = check_pending_migrations()
        
        if has_pending:
            print(f"⚠️  {message}")
            print("🚀 Executando migrations...")
            command.upgrade(alembic_cfg, "head")
            print("✅ Migrations executadas com sucesso!")
            return True
        else:
            print(f"✅ {message}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar migrations: {e}")
        raise


def create_migration(message: str, autogenerate: bool = True):
    """Cria uma nova migration"""
    try:
        alembic_cfg = get_alembic_config()
        
        print(f"📝 Criando migration: {message}")
        
        if autogenerate:
            command.revision(
                alembic_cfg,
                message=message,
                autogenerate=True
            )
        else:
            command.revision(
                alembic_cfg,
                message=message
            )
        
        print("✅ Migration criada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar migration: {e}")
        raise


def downgrade_migration(revision: str = "-1"):
    """Desfaz uma migration"""
    try:
        alembic_cfg = get_alembic_config()
        
        print(f"⏪ Desfazendo migration para: {revision}")
        command.downgrade(alembic_cfg, revision)
        print("✅ Migration desfeita com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao desfazer migration: {e}")
        raise


def show_current_revision():
    """Mostra a revisão atual do banco de dados"""
    try:
        alembic_cfg = get_alembic_config()
        command.current(alembic_cfg)
    except Exception as e:
        print(f"❌ Erro ao obter revisão atual: {e}")
        raise


def show_migration_history():
    """Mostra o histórico de migrations"""
    try:
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg)
    except Exception as e:
        print(f"❌ Erro ao obter histórico: {e}")
        raise


if __name__ == "__main__":
    # Permite executar este arquivo diretamente para rodar migrations
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciador de migrations do Alembic")
    parser.add_argument(
        "action",
        choices=["upgrade", "downgrade", "create", "current", "history", "check"],
        help="Ação a ser executada"
    )
    parser.add_argument(
        "-m", "--message",
        help="Mensagem da migration (usado com create)"
    )
    parser.add_argument(
        "-r", "--revision",
        default="-1",
        help="Revisão alvo (usado com downgrade)"
    )
    parser.add_argument(
        "--no-autogenerate",
        action="store_true",
        help="Não usar autogenerate ao criar migration"
    )
    
    args = parser.parse_args()
    
    if args.action == "upgrade":
        run_migrations()
    elif args.action == "downgrade":
        downgrade_migration(args.revision)
    elif args.action == "create":
        if not args.message:
            print("❌ Erro: --message é obrigatório para criar uma migration")
            sys.exit(1)
        create_migration(args.message, not args.no_autogenerate)
    elif args.action == "current":
        show_current_revision()
    elif args.action == "history":
        show_migration_history()
    elif args.action == "check":
        has_pending, message = check_pending_migrations()
        print(message)
        sys.exit(1 if has_pending else 0)

