"""
Módulo core: Configurações, banco de dados e utilitários centrais
"""
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .migrations import check_pending_migrations, run_migrations

__all__ = [
    # Configuração
    "settings",
    # Banco de Dados
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    # Migrations
    "check_pending_migrations",
    "run_migrations",
]
