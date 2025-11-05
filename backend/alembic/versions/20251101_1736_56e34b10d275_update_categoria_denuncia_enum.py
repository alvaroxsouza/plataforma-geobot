"""update_categoria_denuncia_enum

Revision ID: 56e34b10d275
Revises: 4896404f4fba
Create Date: 2025-11-01 17:36:24.585812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56e34b10d275'
down_revision: Union[str, None] = '4896404f4fba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar o novo enum com os valores corretos
    op.execute("""
        CREATE TYPE categoriadenuncia AS ENUM (
            'calcada', 'rua', 'ciclovia', 'semaforo', 'sinalizacao',
            'iluminacao', 'lixo_entulho', 'poluicao', 'barulho', 'outros'
        );
    """)


def downgrade() -> None:
    # Remover o enum novo
    op.execute("DROP TYPE IF EXISTS categoriadenuncia;")
    
    # Recriar o enum antigo
    op.execute("""
        CREATE TYPE categoriadenuncia AS ENUM (
            'ambiental', 'sanitaria', 'construcao_irregular', 
            'poluicao_sonora', 'outros'
        );
    """)

