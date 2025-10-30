"""Criar tabela arquivos

Revision ID: 010
Revises: 009
Create Date: 2025-10-29 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    op.create_table(
        'arquivos',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('nome_arquivo', sa.String(length=255), nullable=False),
        sa.Column('tamanho_bytes', sa.BigInteger(), nullable=False),
        sa.Column('tipo_mime', sa.String(length=100), nullable=False),
        sa.Column('extensao', sa.String(length=10), nullable=False),
        sa.Column('chave_storage', sa.String(length=500), nullable=False),
        sa.Column('hash_checksum', sa.String(length=64), nullable=False),
        sa.Column('data_upload', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('chave_storage'),
        sa.CheckConstraint('tamanho_bytes > 0', name='tamanho_valido'),
        schema='geobot_db'
    )

    # Criar índices
    op.create_index('idx_arquivos_hash', 'arquivos', ['hash_checksum'], unique=False, schema='geobot_db')
    op.create_index('idx_arquivos_upload', 'arquivos', [sa.text('data_upload DESC')], unique=False, schema='geobot_db')

    # Adicionar comentários
    op.execute("COMMENT ON TABLE geobot_db.arquivos IS 'Arquivos anexados (imagens, documentos, etc)'")
    op.execute("COMMENT ON COLUMN geobot_db.arquivos.hash_checksum IS 'SHA-256 do arquivo para verificação de integridade'")


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.drop_index('idx_arquivos_upload', table_name='arquivos', schema='geobot_db')
    op.drop_index('idx_arquivos_hash', table_name='arquivos', schema='geobot_db')
    op.drop_table('arquivos', schema='geobot_db')

