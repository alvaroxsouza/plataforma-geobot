"""Inserir dados iniciais (seed)

Revision ID: 013
Revises: 012
Create Date: 2025-10-29 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '013'
down_revision: Union[str, None] = '012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    # Inserir grupos padrão
    op.execute("""
        INSERT INTO geobot_db.grupos (nome, descricao) VALUES
            ('Administradores', 'Acesso total ao sistema'),
            ('Fiscais', 'Responsáveis por fiscalizações'),
            ('Cidadãos', 'Usuários que podem fazer denúncias')
    """)

    # Inserir roles padrão
    op.execute("""
        INSERT INTO geobot_db.roles (nome, descricao) VALUES
            ('admin', 'Administração completa'),
            ('fiscalizar', 'Criar e gerenciar fiscalizações'),
            ('denunciar', 'Criar denúncias'),
            ('visualizar_denuncias', 'Visualizar denúncias'),
            ('gerenciar_usuarios', 'Gerenciar usuários do sistema')
    """)

    # Relacionamento Grupo-Role: Administradores têm todas as roles
    op.execute("""
        INSERT INTO geobot_db.grupo_role (grupo_id, role_id)
        SELECT g.id, r.id 
        FROM geobot_db.grupos g, geobot_db.roles r 
        WHERE g.nome = 'Administradores'
    """)

    # Relacionamento Grupo-Role: Fiscais
    op.execute("""
        INSERT INTO geobot_db.grupo_role (grupo_id, role_id)
        SELECT g.id, r.id 
        FROM geobot_db.grupos g, geobot_db.roles r 
        WHERE g.nome = 'Fiscais' AND r.nome IN ('fiscalizar', 'visualizar_denuncias')
    """)

    # Relacionamento Grupo-Role: Cidadãos
    op.execute("""
        INSERT INTO geobot_db.grupo_role (grupo_id, role_id)
        SELECT g.id, r.id 
        FROM geobot_db.grupos g, geobot_db.roles r 
        WHERE g.nome = 'Cidadãos' AND r.nome IN ('denunciar', 'visualizar_denuncias')
    """)


def downgrade() -> None:
    op.execute("SET search_path TO geobot_db, public")

    # Remover relacionamentos
    op.execute("DELETE FROM geobot_db.grupo_role")

    # Remover roles
    op.execute("DELETE FROM geobot_db.roles")

    # Remover grupos
    op.execute("DELETE FROM geobot_db.grupos")
"""Criar schema e extensões

Revision ID: 001
Revises: 
Create Date: 2025-10-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar schema
    op.execute("CREATE SCHEMA IF NOT EXISTS geobot_db")

    # Definir search_path
    op.execute("SET search_path TO geobot_db, public")

    # Criar extensões
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')


def downgrade() -> None:
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    op.execute("DROP SCHEMA IF EXISTS geobot_db CASCADE")

