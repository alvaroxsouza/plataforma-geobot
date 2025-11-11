"""move_tables_to_geobot_schema

Revision ID: d5e9f8a1b2c3
Revises: a796616d1346
Create Date: 2025-11-11 15:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5e9f8a1b2c3'
down_revision: Union[str, None] = 'a796616d1346'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Move todas as tabelas para o schema geobot"""
    
    # 1. Criar o schema geobot
    op.execute('CREATE SCHEMA IF NOT EXISTS geobot')
    
    # 2. Mover os tipos ENUM para o novo schema ANTES das tabelas
    # porque as tabelas dependem desses tipos
    enum_types = ['categoria_denuncia', 'status_denuncia', 'prioridade', 
                  'status_fiscalizacao', 'tipo_analise']
    
    for enum_type in enum_types:
        # Verificar se o tipo existe no schema public antes de mover
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_type t
                    JOIN pg_namespace n ON t.typnamespace = n.oid
                    WHERE t.typname = '{enum_type}' AND n.nspname = 'public'
                ) THEN
                    ALTER TYPE public.{enum_type} SET SCHEMA geobot;
                END IF;
            END $$;
        """)
    
    # 3. Mover as tabelas para o novo schema (em ordem para respeitar dependências)
    # Tabelas independentes primeiro
    op.execute('ALTER TABLE IF EXISTS public.arquivos SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.enderecos SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.grupos SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.roles SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.usuarios SET SCHEMA geobot')
    
    # Tabelas dependentes
    op.execute('ALTER TABLE IF EXISTS public.denuncias SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.grupo_role SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.usuario_grupo SET SCHEMA geobot')
    
    # Tabelas que dependem de denuncias
    op.execute('ALTER TABLE IF EXISTS public.arquivos_denuncia SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.fiscalizacoes SET SCHEMA geobot')
    
    # Tabelas que dependem de fiscalizacoes
    op.execute('ALTER TABLE IF EXISTS public.analises SET SCHEMA geobot')
    op.execute('ALTER TABLE IF EXISTS public.arquivos_fiscalizacao SET SCHEMA geobot')
    
    # Tabelas que dependem de analises
    op.execute('ALTER TABLE IF EXISTS public.arquivos_analise SET SCHEMA geobot')
    
    # 4. As sequences são movidas automaticamente com as tabelas
    # Os índices também são movidos automaticamente com as tabelas
    
    # 5. Comentário no schema
    op.execute("COMMENT ON SCHEMA geobot IS 'Schema principal da plataforma GeoBot'")


def downgrade() -> None:
    """Reverte as tabelas para o schema public"""
    
    # 1. Mover os tipos ENUM de volta para o public
    op.execute('ALTER TYPE geobot.categoria_denuncia SET SCHEMA public')
    op.execute('ALTER TYPE geobot.status_denuncia SET SCHEMA public')
    op.execute('ALTER TYPE geobot.prioridade SET SCHEMA public')
    op.execute('ALTER TYPE geobot.status_fiscalizacao SET SCHEMA public')
    op.execute('ALTER TYPE geobot.tipo_analise SET SCHEMA public')
    
    # 3. Mover as tabelas de volta (ordem inversa para respeitar dependências)
    # Tabelas mais dependentes primeiro
    op.execute('ALTER TABLE geobot.arquivos_analise SET SCHEMA public')
    
    # Tabelas que dependem de fiscalizacoes
    op.execute('ALTER TABLE geobot.arquivos_fiscalizacao SET SCHEMA public')
    op.execute('ALTER TABLE geobot.analises SET SCHEMA public')
    
    # Tabelas que dependem de denuncias
    op.execute('ALTER TABLE geobot.fiscalizacoes SET SCHEMA public')
    op.execute('ALTER TABLE geobot.arquivos_denuncia SET SCHEMA public')
    
    # Tabelas dependentes
    op.execute('ALTER TABLE geobot.usuario_grupo SET SCHEMA public')
    op.execute('ALTER TABLE geobot.grupo_role SET SCHEMA public')
    op.execute('ALTER TABLE geobot.denuncias SET SCHEMA public')
    
    # Tabelas independentes
    op.execute('ALTER TABLE geobot.usuarios SET SCHEMA public')
    op.execute('ALTER TABLE geobot.roles SET SCHEMA public')
    op.execute('ALTER TABLE geobot.grupos SET SCHEMA public')
    op.execute('ALTER TABLE geobot.enderecos SET SCHEMA public')
    op.execute('ALTER TABLE geobot.arquivos SET SCHEMA public')
    
    # 4. Remover o schema geobot (opcional, somente se vazio)
    op.execute('DROP SCHEMA IF EXISTS geobot CASCADE')
