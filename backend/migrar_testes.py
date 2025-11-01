#!/usr/bin/env python3
"""
Script para mover os arquivos de teste antigos para o diretório tests/legacy/
e orientar sobre a nova estrutura de testes.
"""
import os
import shutil
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Arquivos de teste antigos
ARQUIVOS_ANTIGOS = [
    "test_auth.py",
    "test_setup.py"
]

# Diretório de destino
LEGACY_DIR = BASE_DIR / "tests" / "legacy"


def main():
    print("=" * 70)
    print("🔄 MIGRAÇÃO DE ARQUIVOS DE TESTE")
    print("=" * 70)
    print()
    
    # Criar diretório legacy se não existir
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Mover arquivos antigos
    movidos = []
    for arquivo in ARQUIVOS_ANTIGOS:
        caminho_origem = BASE_DIR / arquivo
        if caminho_origem.exists():
            caminho_destino = LEGACY_DIR / arquivo
            shutil.move(str(caminho_origem), str(caminho_destino))
            movidos.append(arquivo)
            print(f"✅ Movido: {arquivo} → tests/legacy/{arquivo}")
    
    if not movidos:
        print("ℹ️  Nenhum arquivo de teste antigo encontrado na raiz.")
    
    print()
    print("=" * 70)
    print("📚 NOVA ESTRUTURA DE TESTES")
    print("=" * 70)
    print()
    print("Os testes agora estão organizados em:")
    print()
    print("  tests/")
    print("  ├── conftest.py              # Fixtures globais")
    print("  ├── integration/             # Testes HTTP (TestClient)")
    print("  │   ├── test_auth.py         # ✅ Criado")
    print("  │   └── test_denuncias.py    # ✅ Criado")
    print("  ├── unit/                    # Testes de lógica isolada")
    print("  │   ├── test_denuncia_service.py  # ✅ Criado")
    print("  │   └── test_denuncia_dtos.py     # ✅ Criado")
    print("  └── legacy/                  # Scripts antigos")
    print("      ├── test_auth.py         # Script HTTP manual")
    print("      └── test_setup.py        # Script de validação")
    print()
    print("=" * 70)
    print("🚀 PRÓXIMOS PASSOS")
    print("=" * 70)
    print()
    print("1. Instalar dependências de teste:")
    print("   pip install pytest pytest-cov")
    print()
    print("2. Executar todos os testes:")
    print("   pytest")
    print()
    print("3. Executar com coverage:")
    print("   pytest --cov=src --cov-report=html")
    print()
    print("4. Consultar documentação:")
    print("   cat tests/README.md")
    print()
    print("Os scripts legados em tests/legacy/ ainda podem ser usados")
    print("manualmente se necessário, mas os novos testes pytest são")
    print("recomendados para desenvolvimento e CI/CD.")
    print()
    print("=" * 70)
    print("✅ MIGRAÇÃO CONCLUÍDA")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
