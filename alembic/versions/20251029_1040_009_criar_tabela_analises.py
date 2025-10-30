"""Criar tabela analises

Revision ID: 009
Revises: 008
Create Date: 2025-10-29 10:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    op.create_table(
        'analises',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('fiscalizacao_id', sa.BigInteger(), nullable=False),
        sa.Column('tipo_analise', postgresql.ENUM('imagem', 'texto', 'relatorio', 'video',
                                                  name='tipo_analise', schema='geobot_db', create_type=False),
                 nullable=False),
        sa.Column('dados_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('resultado_principal', sa.Text(), nullable=True),
        sa.Column('confianca', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('processado_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.ForeignKeyConstraint(['fiscalizacao_id'], ['geobot_db.fiscalizacoes.id'], name='fk_fiscalizacao', ondelete='CASCADE'),
        sa.CheckConstraint('confianca IS NULL OR (confianca >= 0 AND confianca <= 100)', name='confianca_valida'),
        schema='geobot_db'
    )

    # Criar índices
    op.create_index('idx_analises_fiscalizacao', 'analises', ['fiscalizacao_id'], unique=False, schema='geobot_db')
    op.create_index('idx_analises_tipo', 'analises', ['tipo_analise'], unique=False, schema='geobot_db')
    op.execute("CREATE INDEX idx_analises_dados_gin ON geobot_db.analises USING GIN (dados_json)")

    # Adicionar comentários
    op.execute("COMMENT ON TABLE geobot_db.analises IS 'Análises de IA (visão computacional) sobre fiscalizações'")
    op.execute("COMMENT ON COLUMN geobot_db.analises.confianca IS 'Nível de confiança da análise de IA (0-100%)'")


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.execute("DROP INDEX IF EXISTS geobot_db.idx_analises_dados_gin")
    op.drop_index('idx_analises_tipo', table_name='analises', schema='geobot_db')
    op.drop_index('idx_analises_fiscalizacao', table_name='analises', schema='geobot_db')
    op.drop_table('analises', schema='geobot_db')

