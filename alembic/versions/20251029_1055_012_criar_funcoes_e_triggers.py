"""Criar funções e triggers

Revision ID: 012
Revises: 011
Create Date: 2025-10-29 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    # Criar função para atualizar updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION geobot_db.atualizar_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Criar triggers para updated_at
    op.execute("""
        CREATE TRIGGER trigger_usuarios_updated_at
        BEFORE UPDATE ON geobot_db.usuarios
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_grupos_updated_at
        BEFORE UPDATE ON geobot_db.grupos
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_roles_updated_at
        BEFORE UPDATE ON geobot_db.roles
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_enderecos_updated_at
        BEFORE UPDATE ON geobot_db.enderecos
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_denuncias_updated_at
        BEFORE UPDATE ON geobot_db.denuncias
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_fiscalizacoes_updated_at
        BEFORE UPDATE ON geobot_db.fiscalizacoes
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_analises_updated_at
        BEFORE UPDATE ON geobot_db.analises
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_arquivos_updated_at
        BEFORE UPDATE ON geobot_db.arquivos
        FOR EACH ROW EXECUTE FUNCTION geobot_db.atualizar_updated_at();
    """)


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    # Remover triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_arquivos_updated_at ON geobot_db.arquivos")
    op.execute("DROP TRIGGER IF EXISTS trigger_analises_updated_at ON geobot_db.analises")
    op.execute("DROP TRIGGER IF EXISTS trigger_fiscalizacoes_updated_at ON geobot_db.fiscalizacoes")
    op.execute("DROP TRIGGER IF EXISTS trigger_denuncias_updated_at ON geobot_db.denuncias")
    op.execute("DROP TRIGGER IF EXISTS trigger_enderecos_updated_at ON geobot_db.enderecos")
    op.execute("DROP TRIGGER IF EXISTS trigger_roles_updated_at ON geobot_db.roles")
    op.execute("DROP TRIGGER IF EXISTS trigger_grupos_updated_at ON geobot_db.grupos")
    op.execute("DROP TRIGGER IF EXISTS trigger_usuarios_updated_at ON geobot_db.usuarios")

    # Remover função
    op.execute("DROP FUNCTION IF EXISTS geobot_db.atualizar_updated_at()")

