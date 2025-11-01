FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
ENV POETRY_VERSION=1.8.0
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

# Copia arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock ./

# Instala dependências do projeto
RUN poetry install --no-interaction --no-ansi --no-root

# Copia o projeto inteiro (inclusive src/)
COPY . .

# Instala o próprio projeto como pacote
RUN poetry install --no-interaction --no-ansi

# Define variável de ambiente para o Dynaconf
ENV GEOBOT_ENV=production

EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.geobot_plataforma_backend.app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
