"""Criar tabela enderecos

Revision ID: 006
Revises: 005
Create Date: 2025-10-29 10:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    op.create_table(
        'enderecos',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('logradouro', sa.String(length=255), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=True),
        sa.Column('complemento', sa.String(length=100), nullable=True),
        sa.Column('bairro', sa.String(length=100), nullable=False),
        sa.Column('cidade', sa.String(length=100), nullable=False),
        sa.Column('estado', sa.String(length=2), nullable=False),
        sa.Column('pais', sa.String(length=2), nullable=False, server_default=sa.text("'BR'")),
        sa.Column('cep', sa.String(length=8), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.CheckConstraint("cep ~ '^\\d{8}$'", name='cep_valido'),
        sa.CheckConstraint('LENGTH(estado) = 2', name='uf_valida'),
        sa.CheckConstraint('latitude IS NULL OR (latitude >= -90 AND latitude <= 90)', name='latitude_valida'),
        sa.CheckConstraint('longitude IS NULL OR (longitude >= -180 AND longitude <= 180)', name='longitude_valida'),
        schema='geobot_db'
    )

    # Criar índices
    op.create_index('idx_enderecos_cep', 'enderecos', ['cep'], unique=False, schema='geobot_db')
    op.create_index('idx_enderecos_cidade_estado', 'enderecos', ['cidade', 'estado'], unique=False, schema='geobot_db')
    op.create_index('idx_enderecos_coordenadas', 'enderecos', ['latitude', 'longitude'], unique=False, schema='geobot_db',
                    postgresql_where=sa.text('latitude IS NOT NULL AND longitude IS NOT NULL'))

    # Adicionar comentário
    op.execute("COMMENT ON TABLE geobot_db.enderecos IS 'Endereços das denúncias'")


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.drop_index('idx_enderecos_coordenadas', table_name='enderecos', schema='geobot_db')
    op.drop_index('idx_enderecos_cidade_estado', table_name='enderecos', schema='geobot_db')
    op.drop_index('idx_enderecos_cep', table_name='enderecos', schema='geobot_db')
    op.drop_table('enderecos', schema='geobot_db')

