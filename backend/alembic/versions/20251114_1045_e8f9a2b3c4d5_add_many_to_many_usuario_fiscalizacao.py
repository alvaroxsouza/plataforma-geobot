"""add_many_to_many_usuario_fiscalizacao

Revision ID: e8f9a2b3c4d5
Revises: 20251113_0000
Create Date: 2025-11-14 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e8f9a2b3c4d5'
down_revision = '20251113_0000_session_management'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Migração para implementar relação Many-to-Many entre Usuário e Fiscalização.
    
    Passos:
    1. Criar tabela de associação usuario_fiscalizacao
    2. Migrar dados existentes (fiscal_id atual vira uma linha na nova tabela)
    3. Remover coluna fiscal_id da tabela fiscalizacoes
    """
    
    # 1. Criar tabela de associação Many-to-Many
    op.create_table(
        'usuario_fiscalizacao',
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('fiscalizacao_id', sa.BigInteger(), nullable=False),
        sa.Column('papel', sa.String(50), nullable=True, comment='Papel do fiscal nesta fiscalização (ex: responsável, auxiliar)'),
        sa.Column('data_atribuicao', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        sa.ForeignKeyConstraint(['usuario_id'], ['geobot.usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fiscalizacao_id'], ['geobot.fiscalizacoes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('usuario_id', 'fiscalizacao_id'),
        
        schema='geobot'
    )
    
    # Criar índices para otimizar queries
    op.create_index(
        'ix_usuario_fiscalizacao_usuario_id',
        'usuario_fiscalizacao',
        ['usuario_id'],
        schema='geobot'
    )
    op.create_index(
        'ix_usuario_fiscalizacao_fiscalizacao_id',
        'usuario_fiscalizacao',
        ['fiscalizacao_id'],
        schema='geobot'
    )
    
    # 2. Migrar dados existentes
    # Para cada fiscalização que tem fiscal_id, criar entrada na tabela de associação
    op.execute("""
        INSERT INTO geobot.usuario_fiscalizacao (usuario_id, fiscalizacao_id, papel, data_atribuicao, created_at)
        SELECT 
            fiscal_id,
            id,
            'responsavel',
            COALESCE(data_inicializacao, created_at),
            created_at
        FROM geobot.fiscalizacoes
        WHERE fiscal_id IS NOT NULL
    """)
    
    # 3. Remover a coluna fiscal_id (agora obsoleta)
    op.drop_constraint('fiscalizacoes_fiscal_id_fkey', 'fiscalizacoes', schema='geobot', type_='foreignkey')
    op.drop_column('fiscalizacoes', 'fiscal_id', schema='geobot')


def downgrade() -> None:
    """
    Reverter a migração (voltar para relação 1-para-N).
    
    ATENÇÃO: Esta reversão pode causar perda de dados se uma fiscalização
    tiver múltiplos fiscais atribuídos (apenas o primeiro será mantido).
    """
    
    # 1. Re-adicionar coluna fiscal_id
    op.add_column(
        'fiscalizacoes',
        sa.Column('fiscal_id', sa.BigInteger(), nullable=True),
        schema='geobot'
    )
    
    # 2. Migrar dados de volta (pegar apenas o primeiro fiscal de cada fiscalização)
    op.execute("""
        WITH primeiro_fiscal AS (
            SELECT DISTINCT ON (fiscalizacao_id) 
                fiscalizacao_id,
                usuario_id
            FROM geobot.usuario_fiscalizacao
            ORDER BY fiscalizacao_id, data_atribuicao ASC
        )
        UPDATE geobot.fiscalizacoes f
        SET fiscal_id = pf.usuario_id
        FROM primeiro_fiscal pf
        WHERE f.id = pf.fiscalizacao_id
    """)
    
    # 3. Tornar coluna obrigatória (NOT NULL)
    op.alter_column('fiscalizacoes', 'fiscal_id', nullable=False, schema='geobot')
    
    # 4. Re-criar foreign key
    op.create_foreign_key(
        'fiscalizacoes_fiscal_id_fkey',
        'fiscalizacoes',
        'usuarios',
        ['fiscal_id'],
        ['id'],
        source_schema='geobot',
        referent_schema='geobot',
        ondelete='RESTRICT'
    )
    
    # 5. Remover tabela de associação
    op.drop_index('ix_usuario_fiscalizacao_fiscalizacao_id', table_name='usuario_fiscalizacao', schema='geobot')
    op.drop_index('ix_usuario_fiscalizacao_usuario_id', table_name='usuario_fiscalizacao', schema='geobot')
    op.drop_table('usuario_fiscalizacao', schema='geobot')
