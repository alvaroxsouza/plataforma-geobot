"""Criar tabela denuncias

Revision ID: 007
Revises: 006
Create Date: 2025-10-29 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    op.create_table(
        'denuncias',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('endereco_id', sa.BigInteger(), nullable=False),
        sa.Column('status', postgresql.ENUM('pendente', 'em_analise', 'em_fiscalizacao', 'concluida', 'arquivada', 'cancelada',
                                           name='status_denuncia', schema='geobot_db', create_type=False),
                 nullable=False, server_default=sa.text("'pendente'")),
        sa.Column('categoria', postgresql.ENUM('ambiental', 'sanitaria', 'construcao_irregular', 'poluicao_sonora', 'outros',
                                               name='categoria_denuncia', schema='geobot_db', create_type=False),
                 nullable=False),
        sa.Column('prioridade', postgresql.ENUM('baixa', 'media', 'alta', 'urgente',
                                                name='prioridade', schema='geobot_db', create_type=False),
                 nullable=False, server_default=sa.text("'media'")),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.ForeignKeyConstraint(['usuario_id'], ['geobot_db.usuarios.id'], name='fk_usuario', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['endereco_id'], ['geobot_db.enderecos.id'], name='fk_endereco', ondelete='RESTRICT'),
        schema='geobot_db'
    )

    # Criar índices
    op.create_index('idx_denuncias_usuario', 'denuncias', ['usuario_id'], unique=False, schema='geobot_db')
    op.create_index('idx_denuncias_endereco', 'denuncias', ['endereco_id'], unique=False, schema='geobot_db')
    op.create_index('idx_denuncias_status', 'denuncias', ['status'], unique=False, schema='geobot_db')
    op.create_index('idx_denuncias_categoria', 'denuncias', ['categoria'], unique=False, schema='geobot_db')
    op.create_index('idx_denuncias_created', 'denuncias', [sa.text('created_at DESC')], unique=False, schema='geobot_db')

    # Adicionar comentário
    op.execute("COMMENT ON TABLE geobot_db.denuncias IS 'Denúncias realizadas por cidadãos'")


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.drop_index('idx_denuncias_created', table_name='denuncias', schema='geobot_db')
    op.drop_index('idx_denuncias_categoria', table_name='denuncias', schema='geobot_db')
    op.drop_index('idx_denuncias_status', table_name='denuncias', schema='geobot_db')
    op.drop_index('idx_denuncias_endereco', table_name='denuncias', schema='geobot_db')
    op.drop_index('idx_denuncias_usuario', table_name='denuncias', schema='geobot_db')
    op.drop_table('denuncias', schema='geobot_db')

