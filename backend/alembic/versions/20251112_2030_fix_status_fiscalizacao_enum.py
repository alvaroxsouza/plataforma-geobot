"""fix_status_fiscalizacao_enum_values

Revision ID: fix_enum_001
Revises: seed001
Create Date: 2025-11-12 20:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fix_enum_001'
down_revision: Union[str, None] = 'seed001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Corrige os valores do enum status_fiscalizacao para minúsculas
    para corresponder ao código Python
    """
    
    # Estratégia: Criar novo enum, migrar dados, substituir
    
    # 1. Criar novo enum temporário com valores corretos
    op.execute("""
        CREATE TYPE geobot.status_fiscalizacao_new AS ENUM (
            'aguardando',
            'em_andamento', 
            'concluida',
            'cancelada'
        )
    """)
    
    # 2. Alterar coluna para usar o novo enum (com conversão)
    op.execute("""
        ALTER TABLE geobot.fiscalizacoes 
        ALTER COLUMN status TYPE geobot.status_fiscalizacao_new
        USING (
            CASE status::text
                WHEN 'AGUARDANDO' THEN 'aguardando'::geobot.status_fiscalizacao_new
                WHEN 'EM_ANDAMENTO' THEN 'em_andamento'::geobot.status_fiscalizacao_new
                WHEN 'CONCLUIDA' THEN 'concluida'::geobot.status_fiscalizacao_new
                WHEN 'CANCELADA' THEN 'cancelada'::geobot.status_fiscalizacao_new
            END
        )
    """)
    
    # 3. Remover enum antigo
    op.execute("DROP TYPE geobot.status_fiscalizacao")
    
    # 4. Renomear novo enum
    op.execute("ALTER TYPE geobot.status_fiscalizacao_new RENAME TO status_fiscalizacao")
    
    print("\n✅ Enum status_fiscalizacao corrigido:")
    print("   AGUARDANDO → aguardando")
    print("   EM_ANDAMENTO → em_andamento")
    print("   CONCLUIDA → concluida")
    print("   CANCELADA → cancelada\n")


def downgrade() -> None:
    """Reverter para valores em maiúsculas"""
    
    # 1. Criar enum com valores em maiúsculas
    op.execute("""
        CREATE TYPE geobot.status_fiscalizacao_new AS ENUM (
            'AGUARDANDO',
            'EM_ANDAMENTO',
            'CONCLUIDA',
            'CANCELADA'
        )
    """)
    
    # 2. Alterar coluna (com conversão reversa)
    op.execute("""
        ALTER TABLE geobot.fiscalizacoes 
        ALTER COLUMN status TYPE geobot.status_fiscalizacao_new
        USING (
            CASE status::text
                WHEN 'aguardando' THEN 'AGUARDANDO'::geobot.status_fiscalizacao_new
                WHEN 'em_andamento' THEN 'EM_ANDAMENTO'::geobot.status_fiscalizacao_new
                WHEN 'concluida' THEN 'CONCLUIDA'::geobot.status_fiscalizacao_new
                WHEN 'cancelada' THEN 'CANCELADA'::geobot.status_fiscalizacao_new
            END
        )
    """)
    
    # 3. Remover enum novo
    op.execute("DROP TYPE geobot.status_fiscalizacao")
    
    # 4. Renomear enum antigo
    op.execute("ALTER TYPE geobot.status_fiscalizacao_new RENAME TO status_fiscalizacao")
