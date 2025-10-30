# Versionamento do Banco de Dados - Alembic

Este projeto usa Alembic para versionamento e migração do banco de dados PostgreSQL.

## Estrutura das Migrations

As migrations estão organizadas por data e ordem sequencial:

```
alembic/versions/
├── 20251029_1000_001_criar_schema_e_extensoes.py
├── 20251029_1005_002_criar_tipos_enumerados.py
├── 20251029_1010_003_criar_tabela_usuarios.py
├── 20251029_1015_004_criar_tabelas_grupos_e_roles.py
├── 20251029_1020_005_criar_tabelas_relacionamento.py
├── 20251029_1025_006_criar_tabela_enderecos.py
├── 20251029_1030_007_criar_tabela_denuncias.py
├── 20251029_1035_008_criar_tabela_fiscalizacoes.py
├── 20251029_1040_009_criar_tabela_analises.py
├── 20251029_1045_010_criar_tabela_arquivos.py
├── 20251029_1050_011_criar_tabelas_relacionamento_arquivos.py
├── 20251029_1055_012_criar_funcoes_e_triggers.py
└── 20251029_1100_013_inserir_dados_iniciais.py
```

## Configuração

1. Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Configure a URL do banco de dados no arquivo `.env`:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/geobot_db
```

## Comandos Úteis

### Visualizar o histórico de migrations
```bash
alembic history
```

### Verificar a versão atual do banco
```bash
alembic current
```

### Aplicar todas as migrations (upgrade para a última versão)
```bash
alembic upgrade head
```

### Aplicar migrations até uma versão específica
```bash
alembic upgrade 003
```

### Reverter a última migration
```bash
alembic downgrade -1
```

### Reverter todas as migrations
```bash
alembic downgrade base
```

### Criar uma nova migration
```bash
alembic revision -m "descrição da migration"
```

### Criar uma migration com autogenerate (comparando com models)
```bash
alembic revision --autogenerate -m "descrição da migration"
```

## Ordem de Execução das Migrations

1. **001** - Criar schema `geobot_db` e extensões (uuid-ossp, pgcrypto)
2. **002** - Criar tipos enumerados (status_denuncia, categoria_denuncia, etc)
3. **003** - Criar tabela `usuarios`
4. **004** - Criar tabelas `grupos` e `roles`
5. **005** - Criar tabelas de relacionamento `usuario_grupo` e `grupo_role`
6. **006** - Criar tabela `enderecos`
7. **007** - Criar tabela `denuncias`
8. **008** - Criar tabela `fiscalizacoes`
9. **009** - Criar tabela `analises`
10. **010** - Criar tabela `arquivos`
11. **011** - Criar tabelas de relacionamento polimórfico de arquivos
12. **012** - Criar funções e triggers para atualização automática de `updated_at`
13. **013** - Inserir dados iniciais (grupos e roles padrão)

## Schema do Banco

O banco utiliza o schema `geobot_db` para todas as tabelas. O `search_path` é configurado automaticamente nas migrations.

## Extensões PostgreSQL Utilizadas

- **uuid-ossp**: Para geração de UUIDs
- **pgcrypto**: Para funções criptográficas

## Tipos de Dados Especiais

- **ENUM**: status_denuncia, categoria_denuncia, prioridade, status_fiscalizacao, tipo_analise
- **UUID**: Identificadores únicos para todas as entidades
- **JSONB**: Armazenamento de dados JSON nas análises
- **TIMESTAMP WITH TIME ZONE**: Para todos os campos de data/hora

## Boas Práticas

1. Sempre revise as migrations antes de aplicá-las em produção
2. Faça backup do banco antes de aplicar migrations
3. Teste as migrations em ambiente de desenvolvimento primeiro
4. Use `alembic downgrade` com cuidado em produção
5. Mantenha as migrations pequenas e focadas em uma tarefa específica

## Troubleshooting

### Erro de conexão com o banco
Verifique se:
- O PostgreSQL está rodando
- As credenciais no `.env` estão corretas
- O banco de dados existe
- O usuário tem permissões adequadas

### Erro ao aplicar migration
```bash
# Verificar o estado atual
alembic current

# Verificar o histórico
alembic history

# Se necessário, marcar manualmente uma versão
alembic stamp head
```

