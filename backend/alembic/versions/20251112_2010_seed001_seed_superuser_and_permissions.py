"""seed_superuser_and_permissions

Revision ID: seed001
Revises: d5e9f8a1b2c3
Create Date: 2025-11-12 20:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, DateTime, BigInteger, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

# revision identifiers, used by Alembic.
revision: str = 'seed001'
down_revision: Union[str, None] = 'd5e9f8a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria o superusuário do sistema:
    - Superusuário: admin@geobot.com
    - Associado ao grupo "Administradores" (já existente)
    
    NOTA: Grupos e roles já existem nas migrations anteriores
    """
    
    # Definir tabelas para inserção
    usuarios_table = table('usuarios',
        column('id', BigInteger),
        column('uuid', UUID),
        column('cpf', String),
        column('nome', String),
        column('email', String),
        column('senha_hash', String),
        column('ativo', Boolean),
        column('tentativas_login', sa.SmallInteger),
        column('created_at', DateTime),
        column('updated_at', DateTime),
        schema='geobot'
    )
    
    usuario_grupo_table = table('usuario_grupo',
        column('usuario_id', BigInteger),
        column('grupo_id', Integer),
        column('created_at', DateTime),
        schema='geobot'
    )
    
    now = datetime.utcnow()
    
    # ========================================================================
    # 1. CRIAR SUPERUSUÁRIO
    # ========================================================================
    # Senha: Admin@2025
    # Hash bcrypt gerado para a senha acima
    senha_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lMXl0e2sJC.u'
    
    op.bulk_insert(usuarios_table, [
        {
            'id': 1,
            'uuid': uuid.uuid4(),
            'cpf': '00000000000',
            'nome': 'Administrador do Sistema',
            'email': 'admin@geobot.com',
            'senha_hash': senha_hash,
            'ativo': True,
            'tentativas_login': 0,
            'created_at': now,
            'updated_at': now,
        }
    ])
    
    # ========================================================================
    # 2. ASSOCIAR SUPERUSUÁRIO AO GRUPO ADMINISTRADORES (ID=1)
    # ========================================================================
    op.bulk_insert(usuario_grupo_table, [
        {
            'usuario_id': 1,
            'grupo_id': 1,
            'created_at': now
        }
    ])
    
    print("\n" + "="*70)
    print("✅ SUPERUSUÁRIO CRIADO COM SUCESSO!")
    print("="*70)
    print("\n📋 CREDENCIAIS DO SUPERUSUÁRIO:")
    print("   Email: admin@geobot.com")
    print("   Senha: Admin@2025")
    print("   CPF: 00000000000")
    print("   Grupo: Administradores")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Use estas credenciais para fazer login")
    print("   2. Configure as permissões (roles) para os grupos no sistema")
    print("   3. Crie outros usuários conforme necessário")
    print("\n" + "="*70 + "\n")


def downgrade() -> None:
    """Remove o superusuário criado"""
    
    # Remover associações
    op.execute("DELETE FROM geobot.usuario_grupo WHERE usuario_id = 1")
    
    # Remover superusuário
    op.execute("DELETE FROM geobot.usuarios WHERE id = 1")
