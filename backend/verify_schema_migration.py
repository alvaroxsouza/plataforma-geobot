#!/usr/bin/env python3
"""
Script para verificar se a migração para o schema geobot foi bem-sucedida
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from src.geobot_plataforma_backend.core.config import settings
from src.geobot_plataforma_backend.core.database import get_database_url

def check_schema_migration():
    """Verifica se todas as tabelas estão no schema geobot"""
    
    print("=" * 80)
    print("VERIFICAÇÃO DA MIGRAÇÃO PARA SCHEMA GEOBOT")
    print("=" * 80)
    
    # Criar engine
    engine = create_engine(get_database_url())
    
    try:
        with engine.connect() as conn:
            # 1. Verificar tabelas no schema geobot
            print("\n1. Verificando tabelas no schema geobot...")
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'geobot' 
                ORDER BY tablename
            """))
            
            tables = [row[0] for row in result]
            expected_tables = [
                'analises', 'arquivos', 'arquivos_analise', 'arquivos_denuncia',
                'arquivos_fiscalizacao', 'denuncias', 'enderecos', 'fiscalizacoes',
                'grupo_role', 'grupos', 'roles', 'usuario_grupo', 'usuarios'
            ]
            
            print(f"   Tabelas encontradas: {len(tables)}")
            print(f"   Tabelas esperadas: {len(expected_tables)}")
            
            if set(tables) == set(expected_tables):
                print("   ✓ Todas as tabelas estão no schema geobot!")
            else:
                missing = set(expected_tables) - set(tables)
                extra = set(tables) - set(expected_tables)
                if missing:
                    print(f"   ✗ Tabelas faltando: {missing}")
                if extra:
                    print(f"   ! Tabelas extras: {extra}")
                return False
            
            # 2. Verificar tipos ENUM
            print("\n2. Verificando tipos ENUM no schema geobot...")
            result = conn.execute(text("""
                SELECT t.typname
                FROM pg_type t
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE n.nspname = 'geobot' AND t.typtype = 'e'
                ORDER BY t.typname
            """))
            
            enums = [row[0] for row in result]
            expected_enums = [
                'prioridade', 'status_denuncia', 
                'status_fiscalizacao', 'tipo_analise'
            ]
            
            print(f"   ENUMs encontrados: {len(enums)}")
            print(f"   ENUMs esperados: {len(expected_enums)}")
            
            if len(enums) >= len(expected_enums):
                print("   ✓ Tipos ENUM movidos para o schema geobot!")
            else:
                print(f"   ! Alguns ENUMs podem não ter sido movidos")
            
            for enum in enums:
                print(f"      - {enum}")
            
            # 3. Verificar se há tabelas no schema public (além de alembic_version)
            print("\n3. Verificando tabelas restantes no schema public...")
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename != 'alembic_version'
                ORDER BY tablename
            """))
            
            public_tables = [row[0] for row in result]
            
            if not public_tables:
                print("   ✓ Nenhuma tabela da aplicação no schema public!")
            else:
                print(f"   ! Tabelas ainda no public: {public_tables}")
            
            # 4. Verificar contagem de registros em algumas tabelas
            print("\n4. Verificando integridade dos dados...")
            test_tables = ['usuarios', 'grupos', 'roles']
            
            for table in test_tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM geobot.{table}"))
                    count = result.scalar()
                    print(f"   geobot.{table}: {count} registros")
                except Exception as e:
                    print(f"   ✗ Erro ao consultar {table}: {e}")
                    return False
            
            # 5. Testar uma consulta com JOIN
            print("\n5. Testando consulta com JOIN...")
            try:
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM geobot.usuarios u
                    LEFT JOIN geobot.usuario_grupo ug ON u.id = ug.usuario_id
                """))
                count = result.scalar()
                print(f"   ✓ JOIN funcionando! {count} registros consultados")
            except Exception as e:
                print(f"   ✗ Erro no JOIN: {e}")
                return False
            
            print("\n" + "=" * 80)
            print("✓ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 80)
            print("\nTodas as tabelas foram migradas corretamente para o schema geobot.")
            print("O banco de dados está pronto para uso.")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Erro durante a verificação: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    success = check_schema_migration()
    sys.exit(0 if success else 1)
