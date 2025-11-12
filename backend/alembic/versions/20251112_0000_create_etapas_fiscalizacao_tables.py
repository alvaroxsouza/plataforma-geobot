"""create_etapas_fiscalizacao_tables

Revision ID: f4e5a1b2c3d4
Revises: d5e9f8a1b2c3
Create Date: 2025-11-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f4e5a1b2c3d4'
down_revision: Union[str, None] = 'd5e9f8a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar ENUM para as etapas de fiscalização (verificar se já existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type t
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE t.typname = 'etapa_fiscalizacao' AND n.nspname = 'geobot') THEN
                CREATE TYPE geobot.etapa_fiscalizacao AS ENUM (
                    'PENDENTE',
                    'SOBREVOO',
                    'ABASTECIMENTO',
                    'ANALISE_IA',
                    'RELATORIO',
                    'CONCLUIDA',
                    'CANCELADA'
                );
            END IF;
        END $$;
    """)

    # Criar ENUM para status do relatório (verificar se já existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type t
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE t.typname = 'status_relatorio_fiscalizacao' AND n.nspname = 'geobot') THEN
                CREATE TYPE geobot.status_relatorio_fiscalizacao AS ENUM (
                    'RASCUNHO',
                    'REVISAO',
                    'APROVADO',
                    'PUBLICADO'
                );
            END IF;
        END $$;
    """)

    # Tabela: etapas_fiscalizacao
    # Tracks progression through the pipeline stages
    op.create_table(
        'etapas_fiscalizacao',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('fiscalizacao_id', sa.BigInteger(), nullable=False),
        sa.Column('etapa', postgresql.ENUM(
            'PENDENTE',
            'SOBREVOO',
            'ABASTECIMENTO',
            'ANALISE_IA',
            'RELATORIO',
            'CONCLUIDA',
            'CANCELADA',
            name='etapa_fiscalizacao',
            schema='geobot',
            create_type=False
        ), nullable=False),
        sa.Column('progresso_percentual', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dados', postgresql.JSON(), nullable=True),
        sa.Column('resultado', postgresql.JSON(), nullable=True),
        sa.Column('erro', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('progresso_percentual >= 0 AND progresso_percentual <= 100', name='progresso_valido'),
        sa.ForeignKeyConstraint(['fiscalizacao_id'], ['geobot.fiscalizacoes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        schema='geobot'
    )
    op.create_index(
        'ix_etapas_fiscalizacao_fiscalizacao_id',
        'etapas_fiscalizacao',
        ['fiscalizacao_id'],
        schema='geobot'
    )
    op.create_index(
        'ix_etapas_fiscalizacao_etapa',
        'etapas_fiscalizacao',
        ['etapa'],
        schema='geobot'
    )

    # Tabela: arquivos_fiscalizacao
    # References to files stored in Azure Blob Storage
    op.create_table(
        'arquivos_fiscalizacao',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('fiscalizacao_id', sa.BigInteger(), nullable=False),
        sa.Column('etapa_id', sa.BigInteger(), nullable=True),
        sa.Column('tipo', sa.String(50), nullable=False),  # 'sobrevoo', 'abastecimento', etc
        sa.Column('url_blob', sa.String(500), nullable=False),
        sa.Column('tamanho_bytes', sa.BigInteger(), nullable=False),
        sa.Column('metadados', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('tamanho_bytes > 0', name='tamanho_arquivo_valido'),
        sa.ForeignKeyConstraint(['fiscalizacao_id'], ['geobot.fiscalizacoes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['etapa_id'], ['geobot.etapas_fiscalizacao.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        schema='geobot'
    )
    op.create_index(
        'ix_arquivos_fiscalizacao_fiscalizacao_id',
        'arquivos_fiscalizacao',
        ['fiscalizacao_id'],
        schema='geobot'
    )
    op.create_index(
        'ix_arquivos_fiscalizacao_etapa_id',
        'arquivos_fiscalizacao',
        ['etapa_id'],
        schema='geobot'
    )
    op.create_index(
        'ix_arquivos_fiscalizacao_tipo',
        'arquivos_fiscalizacao',
        ['tipo'],
        schema='geobot'
    )

    # Tabela: resultados_analise_ia
    # Stores AI analysis results with detections and confidence metrics
    op.create_table(
        'resultados_analise_ia',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('etapa_id', sa.BigInteger(), nullable=False),
        sa.Column('job_id', sa.String(100), nullable=False),  # Skypilot job ID
        sa.Column('deteccoes', postgresql.JSON(), nullable=False),  # Array of detections with bboxes, confidence, class
        sa.Column('confianca_media', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('classificacao_geral', sa.String(50), nullable=False),  # 'anomalia', 'normal', etc
        sa.Column('modelo_utilizado', sa.String(100), nullable=False),  # 'yolov8', etc
        sa.Column('tempo_processamento', sa.Integer(), nullable=False),  # milliseconds
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('confianca_media >= 0 AND confianca_media <= 1', name='confianca_valida'),
        sa.CheckConstraint('tempo_processamento > 0', name='tempo_processamento_valido'),
        sa.ForeignKeyConstraint(['etapa_id'], ['geobot.etapas_fiscalizacao.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id'),
        sa.UniqueConstraint('uuid'),
        schema='geobot'
    )
    op.create_index(
        'ix_resultados_analise_ia_etapa_id',
        'resultados_analise_ia',
        ['etapa_id'],
        schema='geobot'
    )
    op.create_index(
        'ix_resultados_analise_ia_job_id',
        'resultados_analise_ia',
        ['job_id'],
        schema='geobot'
    )

    # Tabela: relatorios_fiscalizacao
    # Generated reports from the analysis
    op.create_table(
        'relatorios_fiscalizacao',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('fiscalizacao_id', sa.BigInteger(), nullable=False),
        sa.Column('etapa_id', sa.BigInteger(), nullable=False),
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('resumo_executivo', sa.Text(), nullable=False),
        sa.Column('conclusoes', sa.Text(), nullable=False),
        sa.Column('recomendacoes', sa.Text(), nullable=True),
        sa.Column('dados_relatorio', postgresql.JSON(), nullable=True),
        sa.Column('url_documento', sa.String(500), nullable=True),
        sa.Column('status', postgresql.ENUM(
            'RASCUNHO',
            'REVISAO',
            'APROVADO',
            'PUBLICADO',
            name='status_relatorio_fiscalizacao',
            schema='geobot',
            create_type=False
        ), nullable=False, server_default='RASCUNHO'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['fiscalizacao_id'], ['geobot.fiscalizacoes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['etapa_id'], ['geobot.etapas_fiscalizacao.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        schema='geobot'
    )
    op.create_index(
        'ix_relatorios_fiscalizacao_fiscalizacao_id',
        'relatorios_fiscalizacao',
        ['fiscalizacao_id'],
        schema='geobot'
    )
    op.create_index(
        'ix_relatorios_fiscalizacao_etapa_id',
        'relatorios_fiscalizacao',
        ['etapa_id'],
        schema='geobot'
    )
    op.create_index(
        'ix_relatorios_fiscalizacao_status',
        'relatorios_fiscalizacao',
        ['status'],
        schema='geobot'
    )


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('relatorios_fiscalizacao', schema='geobot')
    op.drop_table('resultados_analise_ia', schema='geobot')
    op.drop_table('arquivos_fiscalizacao', schema='geobot')
    op.drop_table('etapas_fiscalizacao', schema='geobot')

    # Drop ENUMs
    op.execute('DROP TYPE IF EXISTS geobot.etapa_fiscalizacao CASCADE')
    op.execute('DROP TYPE IF EXISTS geobot.status_relatorio_fiscalizacao CASCADE')
