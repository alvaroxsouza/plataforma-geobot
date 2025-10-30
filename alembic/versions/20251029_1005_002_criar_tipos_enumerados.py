"""Criar tipos enumerados

Revision ID: 002
Revises: 001
Create Date: 2025-10-29 10:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Definir search_path
    op.execute("SET search_path TO geobot_db, public")

    # Criar tipos enumerados
    op.execute("""
        CREATE TYPE geobot_db.status_denuncia AS ENUM (
            'pendente', 'em_analise', 'em_fiscalizacao', 
            'concluida', 'arquivada', 'cancelada'
        )
    """)

    op.execute("""
        CREATE TYPE geobot_db.categoria_denuncia AS ENUM (
            'ambiental', 'sanitaria', 'construcao_irregular', 
            'poluicao_sonora', 'outros'
        )
    """)

    op.execute("""
        CREATE TYPE geobot_db.prioridade AS ENUM (
            'baixa', 'media', 'alta', 'urgente'
        )
    """)

    op.execute("""
        CREATE TYPE geobot_db.status_fiscalizacao AS ENUM (
            'aguardando', 'em_andamento', 'concluida', 'cancelada'
        )
    """)

    op.execute("""
        CREATE TYPE geobot_db.tipo_analise AS ENUM (
            'imagem', 'texto', 'relatorio', 'video'
        )
    """)


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")
    op.execute("DROP TYPE IF EXISTS geobot_db.tipo_analise")
    op.execute("DROP TYPE IF EXISTS geobot_db.status_fiscalizacao")
    op.execute("DROP TYPE IF EXISTS geobot_db.prioridade")
    op.execute("DROP TYPE IF EXISTS geobot_db.categoria_denuncia")
    op.execute("DROP TYPE IF EXISTS geobot_db.status_denuncia")

