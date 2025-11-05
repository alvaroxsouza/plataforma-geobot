"""fix_denuncia_enum_reference

Revision ID: 05d51b29fa7d
Revises: 56e34b10d275
Create Date: 2025-11-01 18:00:52.163360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05d51b29fa7d'
down_revision: Union[str, None] = '56e34b10d275'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove o enum antigo categoria_denuncia da coluna
    op.execute("ALTER TABLE denuncias ALTER COLUMN categoria TYPE VARCHAR(50)")
    
    # Dropa o enum antigo se existir
    op.execute("DROP TYPE IF EXISTS categoria_denuncia CASCADE")
    
    # Altera a coluna para usar o novo enum categoriadenuncia
    op.execute("ALTER TABLE denuncias ALTER COLUMN categoria TYPE categoriadenuncia USING categoria::categoriadenuncia")


def downgrade() -> None:
    # Reverte para VARCHAR caso necessário
    op.execute("ALTER TABLE denuncias ALTER COLUMN categoria TYPE VARCHAR(50)")

