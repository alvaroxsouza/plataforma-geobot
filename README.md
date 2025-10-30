# Geobot Plataforma Backend

Sistema backend para gerenciamento de denúncias e fiscalizações com análise de IA.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Banco de Dados](#banco-de-dados)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Migrations](#migrations)

## 🎯 Sobre o Projeto

Plataforma para gerenciamento de denúncias cidadãs com sistema de fiscalização integrado e análise por IA (visão computacional).

### Funcionalidades Principais

- 🔐 Sistema de autenticação e autorização (usuários, grupos e roles)
- 📝 Gerenciamento de denúncias por categorias
- 🔍 Sistema de fiscalização com protocolos
- 🤖 Análise de IA para imagens, textos e vídeos
- 📁 Upload e gerenciamento de arquivos
- 📍 Geolocalização de denúncias

## 🚀 Tecnologias

- **Python 3.11+**
- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **Alembic** - Versionamento de banco de dados
- **PostgreSQL** - Banco de dados
- **Poetry** - Gerenciamento de dependências
- **Dynaconf** - Gerenciamento de configurações
- **Docker** - Containerização

## 📁 Estrutura do Projeto

```
geobot-plataforma-backend/
├── alembic/                    # Configuração e migrations do Alembic
│   ├── versions/              # Arquivos de migration organizados por data
│   ├── env.py                 # Configuração do ambiente Alembic
├── postgres-init/             # Scripts de inicialização do PostgreSQL
│   ├── script.py.mako         # Template para novas migrations
│   └── README.md              # Documentação das migrations
├── src/
│       ├── core/              # Configurações core
│       │   ├── config.py      # Configuração Dynaconf
│       │   └── database.py    # Configuração do banco de dados
│       ├── api/               # Controllers da API
│       ├── core/              # Configurações core (database, etc)
│       ├── domain/            # Camada de domínio
│       │   ├── entity/        # Entidades de domínio
│       │   ├── repository/    # Interfaces de repositório
│       │   └── service/       # Serviços de domínio
│       └── security/          # Autenticação e autorização
├── static/                    # Arquivos estáticos
├── settings.toml              # Configurações gerais (Dynaconf)
├── .secrets.local.toml        # Secrets locais (NÃO commitado)
├── Dockerfile                 # Imagem Docker
├── docker-compose.yml         # Orquestração Docker
├── templates/                 # Templates HTML
├── app.py                     # Aplicação Flask principal
├── .env.example              # Exemplo de variáveis de ambiente
├── .gitignore                # Arquivos ignorados pelo Git
└── manage_migrations.sh      # Script helper para migrations
```

## 🔧 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL 12 ou superior
- Poetry

### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd geobot-plataforma-backend
```

2. **Instale as dependências**
```bash
poetry install
```

3. **Ative o ambiente virtual**
```bash
poetry shell
```

Este projeto usa **Dynaconf** para gerenciamento de configurações. Veja [DYNACONF.md](DYNACONF.md) para detalhes completos.

### Configuração Local

1. **Configure os secrets**

O arquivo `.secrets.local.toml` já está configurado com as credenciais de desenvolvimento:
```toml
[development]
db_name = "geobot_platform"
db_user = "geobot_user"
db_password = "geobot2025"
db_port = 5433
```

2. **(Opcional) Personalize configurações locais**

# Criar arquivo de configurações locais
nano settings.local.toml
```bash
cp .env.example .env
### Ambientes Disponíveis

- **default** - Configurações base
- **development** - Desenvolvimento local (padrão)
- **production** - Produção
- **testing** - Testes

### Trocar Ambiente
SECRET_KEY=sua-chave-secreta-aqui

# Development (padrão)
python app.py

# Production
GEOBOT_ENV=production python app.py

# Testing
GEOBOT_ENV=testing python app.py
```bash
createdb geobot_db
```

## 🗄️ Banco de Dados

### Schema
## 🐳 Docker

### Início Rápido com Docker

```bash
# 1. Iniciar serviços (PostgreSQL + App)
docker-compose up -d

# 2. Aplicar migrations
docker-compose exec app alembic upgrade head

# 3. Ver logs
docker-compose logs -f app

# 4. Acessar aplicação
curl http://localhost:5000/health
```

Veja [DOCKER.md](DOCKER.md) para documentação completa.


O projeto utiliza o schema `geobot_db` no PostgreSQL com as seguintes tabelas principais:
### Opção 1: Desenvolvimento Local

```bash
# Criar banco de dados
createdb -p 5433 geobot_platform

# Aplicar migrations
GEOBOT_ENV=development alembic upgrade head

# Iniciar aplicação
GEOBOT_ENV=development python app.py
```

### Opção 2: Com Docker (Recomendado)

```bash
# Iniciar tudo
docker-compose up -d

# Aplicar migrations
docker-compose exec app alembic upgrade head
```


- **usuarios** - Usuários do sistema
- **grupos** - Grupos de permissões
- **roles** - Papéis/permissões
- **denuncias** - Denúncias realizadas
- **fiscalizacoes** - Fiscalizações das denúncias
- **analises** - Análises de IA
- **arquivos** - Arquivos anexados
- **enderecos** - Endereços das denúncias

### Extensões PostgreSQL

- `uuid-ossp` - Geração de UUIDs
- `pgcrypto` - Funções criptográficas

### Tipos Enumerados

- `status_denuncia`: pendente, em_analise, em_fiscalizacao, concluida, arquivada, cancelada
- `categoria_denuncia`: ambiental, sanitaria, construcao_irregular, poluicao_sonora, outros
- `prioridade`: baixa, media, alta, urgente
- `status_fiscalizacao`: aguardando, em_andamento, concluida, cancelada
- `tipo_analise`: imagem, texto, relatorio, video

## 🚀 Uso

### Aplicar Migrations

**Opção 1: Usando o script helper (recomendado)**
```bash
./manage_migrations.sh
```

**Opção 2: Comandos Alembic diretos**
```bash
# Aplicar todas as migrations
alembic upgrade head

# Ver histórico
alembic history

# Ver versão atual
alembic current

# Reverter última migration
alembic downgrade -1
```

### Iniciar o servidor

```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```
GET /health
```
Verifica o status da aplicação e conexão com banco de dados.

**Resposta:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Informações da API
```
GET /
```
Retorna informações básicas sobre a API.

```
## 📚 Documentação Adicional

- [DYNACONF.md](DYNACONF.md) - Guia completo do Dynaconf (configurações)
- [DOCKER.md](DOCKER.md) - Guia completo do Docker
- [alembic/README.md](alembic/README.md) - Documentação das migrations
- [COMANDOS.md](COMANDOS.md) - Referência de comandos
- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Guia de início rápido
- [RESUMO_DYNACONF_DOCKER.md](RESUMO_DYNACONF_DOCKER.md) - Resumo da configuração

GET /api/v1/
```
Retorna informações sobre a versão da API.

## 🔄 Migrations

As migrations estão organizadas por data e ordem sequencial:

1. **001** - Schema e extensões
2. **002** - Tipos enumerados
3. **003** - Tabela usuarios
4. **004** - Tabelas grupos e roles
5. **005** - Relacionamentos usuario_grupo e grupo_role
6. **006** - Tabela enderecos
7. **007** - Tabela denuncias
8. **008** - Tabela fiscalizacoes
9. **009** - Tabela analises
10. **010** - Tabela arquivos
11. **011** - Relacionamentos polimórficos de arquivos
12. **012** - Funções e triggers
13. **013** - Dados iniciais (seed)

Para mais detalhes sobre migrations, consulte [alembic/README.md](alembic/README.md)

## 📝 Dados Iniciais

Após aplicar as migrations, os seguintes dados iniciais são inseridos:

### Grupos
- **Administradores** - Acesso total ao sistema
- **Fiscais** - Responsáveis por fiscalizações
- **Cidadãos** - Usuários que podem fazer denúncias

### Roles
- **admin** - Administração completa
- **fiscalizar** - Criar e gerenciar fiscalizações
- **denunciar** - Criar denúncias
- **visualizar_denuncias** - Visualizar denúncias
- **gerenciar_usuarios** - Gerenciar usuários do sistema

## 🛠️ Desenvolvimento

### Criar nova migration

```bash
alembic revision -m "descrição da migration"
```

### Validar código
```bash
# Verificar erros
poetry run flake8

# Formatar código
poetry run black .
```

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.

## 👥 Autores

- Álvaro Souza Oliveira

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

