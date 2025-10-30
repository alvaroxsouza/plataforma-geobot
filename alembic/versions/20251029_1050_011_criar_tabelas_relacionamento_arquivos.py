"""Criar tabelas de relacionamento polimórfico de arquivos

Revision ID: 011
Revises: 010
Create Date: 2025-10-29 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    # Tabela arquivos_denuncia
    op.create_table(
        'arquivos_denuncia',
        sa.Column('arquivo_id', sa.BigInteger(), nullable=False),
        sa.Column('denuncia_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('arquivo_id', 'denuncia_id'),
        sa.ForeignKeyConstraint(['arquivo_id'], ['geobot_db.arquivos.id'], name='fk_arquivo', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['denuncia_id'], ['geobot_db.denuncias.id'], name='fk_denuncia', ondelete='CASCADE'),
        schema='geobot_db'
    )

    # Tabela arquivos_fiscalizacao
    op.create_table(
        'arquivos_fiscalizacao',
        sa.Column('arquivo_id', sa.BigInteger(), nullable=False),
        sa.Column('fiscalizacao_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('arquivo_id', 'fiscalizacao_id'),
        sa.ForeignKeyConstraint(['arquivo_id'], ['geobot_db.arquivos.id'], name='fk_arquivo', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fiscalizacao_id'], ['geobot_db.fiscalizacoes.id'], name='fk_fiscalizacao', ondelete='CASCADE'),
        schema='geobot_db'
    )

    # Tabela arquivos_analise
    op.create_table(
        'arquivos_analise',
        sa.Column('arquivo_id', sa.BigInteger(), nullable=False),
        sa.Column('analise_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('arquivo_id', 'analise_id'),
        sa.ForeignKeyConstraint(['arquivo_id'], ['geobot_db.arquivos.id'], name='fk_arquivo', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['analise_id'], ['geobot_db.analises.id'], name='fk_analise', ondelete='CASCADE'),
        schema='geobot_db'
    )


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.drop_table('arquivos_analise', schema='geobot_db')
    op.drop_table('arquivos_fiscalizacao', schema='geobot_db')
    op.drop_table('arquivos_denuncia', schema='geobot_db')

