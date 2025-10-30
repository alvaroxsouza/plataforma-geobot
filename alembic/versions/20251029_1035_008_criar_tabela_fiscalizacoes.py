"""Criar tabela fiscalizacoes

Revision ID: 008
Revises: 007
Create Date: 2025-10-29 10:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    op.create_table(
        'fiscalizacoes',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('denuncia_id', sa.BigInteger(), nullable=False),
        sa.Column('fiscal_id', sa.BigInteger(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('status', postgresql.ENUM('aguardando', 'em_andamento', 'concluida', 'cancelada',
                                           name='status_fiscalizacao', schema='geobot_db', create_type=False),
                 nullable=False, server_default=sa.text("'aguardando'")),
        sa.Column('data_inicializacao', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_conclusao', sa.DateTime(timezone=True), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('codigo'),
        sa.ForeignKeyConstraint(['denuncia_id'], ['geobot_db.denuncias.id'], name='fk_denuncia', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['fiscal_id'], ['geobot_db.usuarios.id'], name='fk_fiscal', ondelete='RESTRICT'),
        sa.CheckConstraint('data_conclusao IS NULL OR data_conclusao >= data_inicializacao', name='datas_validas'),
        schema='geobot_db'
    )

    # Criar índices
    op.create_index('idx_fiscalizacoes_denuncia', 'fiscalizacoes', ['denuncia_id'], unique=False, schema='geobot_db')
    op.create_index('idx_fiscalizacoes_fiscal', 'fiscalizacoes', ['fiscal_id'], unique=False, schema='geobot_db')
    op.create_index('idx_fiscalizacoes_status', 'fiscalizacoes', ['status'], unique=False, schema='geobot_db')
    op.create_index('idx_fiscalizacoes_codigo', 'fiscalizacoes', ['codigo'], unique=False, schema='geobot_db')

    # Adicionar comentários
    op.execute("COMMENT ON TABLE geobot_db.fiscalizacoes IS 'Fiscalizações realizadas em resposta às denúncias'")
    op.execute("COMMENT ON COLUMN geobot_db.fiscalizacoes.codigo IS 'Código único de protocolo da fiscalização'")


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.drop_index('idx_fiscalizacoes_codigo', table_name='fiscalizacoes', schema='geobot_db')
    op.drop_index('idx_fiscalizacoes_status', table_name='fiscalizacoes', schema='geobot_db')
    op.drop_index('idx_fiscalizacoes_fiscal', table_name='fiscalizacoes', schema='geobot_db')
    op.drop_index('idx_fiscalizacoes_denuncia', table_name='fiscalizacoes', schema='geobot_db')
    op.drop_table('fiscalizacoes', schema='geobot_db')

