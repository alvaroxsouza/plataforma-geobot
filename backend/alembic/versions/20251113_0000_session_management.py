"""create session management table

Revision ID: 20251113_0000_session_management
Revises: 20251112_2030_fix_status_fiscalizacao_enum
Create Date: 2025-11-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251113_0000_session_management'
down_revision = '20251112_2030_fix_status_fiscalizacao_enum'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela de sessões
    op.create_table(
        'sessoes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('refresh_token_hash', sa.String(255), nullable=True),
        sa.Column('device_name', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('criada_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ultima_atividade', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expira_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ativa', sa.Boolean(), nullable=False),
        sa.Column('revogada_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('motivo_revogacao', sa.String(255), nullable=True),
        sa.Column('refresh_token_expira_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('proxima_renovacao_permitida_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tentativas_renovacao', sa.BigInteger(), nullable=False),
        sa.Column('tentativas_acesso_invalido', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['geobot.usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('token_hash'),
        sa.UniqueConstraint('refresh_token_hash'),
        schema='geobot'
    )
    
    # Criar índices para melhorar performance
    op.create_index(
        'idx_sessoes_usuario_id',
        'sessoes',
        ['usuario_id'],
        schema='geobot'
    )
    op.create_index(
        'idx_sessoes_token_hash',
        'sessoes',
        ['token_hash'],
        schema='geobot'
    )
    op.create_index(
        'idx_sessoes_refresh_token_hash',
        'sessoes',
        ['refresh_token_hash'],
        schema='geobot'
    )
    op.create_index(
        'idx_sessoes_ativa_expira',
        'sessoes',
        ['ativa', 'expira_em'],
        schema='geobot'
    )


def downgrade() -> None:
    # Remover índices
    op.drop_index('idx_sessoes_ativa_expira', schema='geobot')
    op.drop_index('idx_sessoes_refresh_token_hash', schema='geobot')
    op.drop_index('idx_sessoes_token_hash', schema='geobot')
    op.drop_index('idx_sessoes_usuario_id', schema='geobot')
    
    # Remover tabela
    op.drop_table('sessoes', schema='geobot')
