"""
Configuração do banco de dados
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Construir URL do banco de dados a partir das configurações
def get_database_url():
    """Constrói a URL do banco de dados a partir das configurações"""
    db_password = getattr(settings, 'db_password', '')

    if db_password:
        return (
            f"postgresql://{settings.db_user}:{db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
    else:
        return (
            f"postgresql://{settings.db_user}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )

DATABASE_URL = get_database_url()

# Criar engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=settings.get('db_pool_pre_ping', True),
    pool_size=settings.get('db_pool_size', 10),
    max_overflow=settings.get('db_max_overflow', 20),
    echo=settings.get('db_echo', False)
)

# Criar SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os models
Base = declarative_base()


def get_db():
    """
    Dependency que cria uma sessão de banco de dados
    e garante que ela seja fechada após o uso
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa o banco de dados
    Útil para testes ou setup inicial
    """
    Base.metadata.create_all(bind=engine)


def check_db_connection():
    """
    Verifica a conexão com o banco de dados
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        return False

