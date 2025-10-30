"""Criar tabelas de relacionamento usuario_grupo e grupo_role

Revision ID: 005
Revises: 004
Create Date: 2025-10-29 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    # Tabela usuario_grupo (N:N)
    op.create_table(
        'usuario_grupo',
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('grupo_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('usuario_id', 'grupo_id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['geobot_db.usuarios.id'], name='fk_usuario', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['grupo_id'], ['geobot_db.grupos.id'], name='fk_grupo', ondelete='CASCADE'),
        schema='geobot_db'
    )

    # Tabela grupo_role (N:N)
    op.create_table(
        'grupo_role',
        sa.Column('grupo_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('grupo_id', 'role_id'),
        sa.ForeignKeyConstraint(['grupo_id'], ['geobot_db.grupos.id'], name='fk_grupo', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['geobot_db.roles.id'], name='fk_role', ondelete='CASCADE'),
        schema='geobot_db'
    )


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.drop_table('grupo_role', schema='geobot_db')
    op.drop_table('usuario_grupo', schema='geobot_db')

