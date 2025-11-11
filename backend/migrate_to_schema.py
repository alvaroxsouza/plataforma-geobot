#!/usr/bin/env python3
"""
Script para executar a migração para o schema geobot
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from alembic import command
from alembic.config import Config

def main():
    """Executa a migração para o schema geobot"""
    # Configurar Alembic
    alembic_cfg = Config("alembic.ini")
    
    print("=" * 80)
    print("MIGRAÇÃO PARA SCHEMA GEOBOT")
    print("=" * 80)
    
    # Verificar o status atual
    print("\n1. Status atual das migrações:")
    try:
        command.current(alembic_cfg, verbose=True)
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        return 1
    
    # Executar a migração
    print("\n2. Executando migração para o schema geobot...")
    try:
        command.upgrade(alembic_cfg, "head")
        print("✓ Migração executada com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao executar migração: {e}")
        return 1
    
    # Verificar o novo status
    print("\n3. Status após a migração:")
    try:
        command.current(alembic_cfg, verbose=True)
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        return 1
    
    print("\n" + "=" * 80)
    print("MIGRAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print("\nTodas as tabelas agora estão no schema 'geobot'")
    print("Para acessá-las no SQL, use: geobot.nome_da_tabela")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
