"""Criar tabela usuarios

Revision ID: 003
Revises: 002
Create Date: 2025-10-29 10:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    op.create_table(
        'usuarios',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('cpf', sa.String(length=11), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('senha_hash', sa.String(length=255), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('data_ultimo_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tentativas_login', sa.SmallInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('bloqueado_ate', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('cpf'),
        sa.UniqueConstraint('email'),
        sa.CheckConstraint("cpf ~ '^\\d{11}$'", name='cpf_valido'),
        sa.CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='email_valido'),
        sa.CheckConstraint('tentativas_login >= 0 AND tentativas_login <= 5', name='tentativas_validas'),
        schema='geobot_db'
    )

    # Criar índices
    op.create_index('idx_usuarios_cpf', 'usuarios', ['cpf'], unique=False, schema='geobot_db',
                    postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_usuarios_email', 'usuarios', ['email'], unique=False, schema='geobot_db',
                    postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_usuarios_ativo', 'usuarios', ['ativo'], unique=False, schema='geobot_db',
                    postgresql_where=sa.text('deleted_at IS NULL'))

    # Adicionar comentário
    op.execute("COMMENT ON TABLE geobot_db.usuarios IS 'Usuários do sistema com autenticação e controle de acesso'")
    op.execute("COMMENT ON COLUMN geobot_db.usuarios.bloqueado_ate IS 'Data até quando o usuário está bloqueado por tentativas de login'")


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.drop_index('idx_usuarios_ativo', table_name='usuarios', schema='geobot_db')
    op.drop_index('idx_usuarios_email', table_name='usuarios', schema='geobot_db')
    op.drop_index('idx_usuarios_cpf', table_name='usuarios', schema='geobot_db')
    op.drop_table('usuarios', schema='geobot_db')

