"""fix_fiscalizacao_and_analise_enums

Revision ID: fix_fiscalizacao_enums
Revises: d5e9f8a1b2c3
Create Date: 2025-11-12 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_fiscalizacao_enums'
down_revision: Union[str, None] = 'd5e9f8a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Converter colunas para VARCHAR temporariamente
    op.execute("ALTER TABLE geobot.fiscalizacoes ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("ALTER TABLE geobot.analises ALTER COLUMN tipo_analise TYPE VARCHAR(50)")
    
    # Dropar enums antigos
    op.execute("DROP TYPE IF EXISTS geobot.status_fiscalizacao CASCADE")
    op.execute("DROP TYPE IF EXISTS geobot.tipo_analise CASCADE")
    
    # Recriar enums com valores em minúsculas
    op.execute("""
        CREATE TYPE geobot.status_fiscalizacao AS ENUM (
            'aguardando', 'em_andamento', 'concluida', 'cancelada'
        )
    """)
    op.execute("""
        CREATE TYPE geobot.tipo_analise AS ENUM (
            'imagem', 'texto', 'relatorio', 'video'
        )
    """)
    
    # Converter dados existentes para minúsculas
    op.execute("""
        UPDATE geobot.fiscalizacoes 
        SET status = LOWER(status)
    """)
    op.execute("""
        UPDATE geobot.analises 
        SET tipo_analise = LOWER(tipo_analise)
    """)
    
    # Converter colunas de volta para usar os novos enums
    op.execute("ALTER TABLE geobot.fiscalizacoes ALTER COLUMN status TYPE geobot.status_fiscalizacao USING status::geobot.status_fiscalizacao")
    op.execute("ALTER TABLE geobot.analises ALTER COLUMN tipo_analise TYPE geobot.tipo_analise USING tipo_analise::geobot.tipo_analise")


def downgrade() -> None:
    # Reverte para VARCHAR caso necessário
    op.execute("ALTER TABLE geobot.fiscalizacoes ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("ALTER TABLE geobot.analises ALTER COLUMN tipo_analise TYPE VARCHAR(50)")

