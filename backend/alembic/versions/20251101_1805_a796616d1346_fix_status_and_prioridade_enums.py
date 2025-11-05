"""fix_status_and_prioridade_enums

Revision ID: a796616d1346
Revises: 05d51b29fa7d
Create Date: 2025-11-01 18:05:50.217183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a796616d1346'
down_revision: Union[str, None] = '05d51b29fa7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Converter colunas para VARCHAR temporariamente
    op.execute("ALTER TABLE denuncias ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("ALTER TABLE denuncias ALTER COLUMN prioridade TYPE VARCHAR(50)")
    
    # Dropar enums antigos
    op.execute("DROP TYPE IF EXISTS status_denuncia CASCADE")
    op.execute("DROP TYPE IF EXISTS prioridade CASCADE")
    
    # Recriar enums com valores em minúsculas
    op.execute("""
        CREATE TYPE status_denuncia AS ENUM (
            'pendente', 'em_analise', 'em_fiscalizacao', 
            'concluida', 'arquivada', 'cancelada'
        )
    """)
    op.execute("""
        CREATE TYPE prioridade AS ENUM (
            'baixa', 'media', 'alta', 'urgente'
        )
    """)
    
    # Converter dados existentes para minúsculas
    op.execute("""
        UPDATE denuncias 
        SET status = LOWER(status),
            prioridade = LOWER(prioridade)
    """)
    
    # Converter colunas de volta para usar os novos enums
    op.execute("ALTER TABLE denuncias ALTER COLUMN status TYPE status_denuncia USING status::status_denuncia")
    op.execute("ALTER TABLE denuncias ALTER COLUMN prioridade TYPE prioridade USING prioridade::prioridade")


def downgrade() -> None:
    # Reverte para VARCHAR caso necessário
    op.execute("ALTER TABLE denuncias ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("ALTER TABLE denuncias ALTER COLUMN prioridade TYPE VARCHAR(50)")

