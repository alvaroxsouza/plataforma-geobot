"""FastAPI entrypoint para a API Geobot Plataforma
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.geobot_plataforma_backend.core.config import settings
from src.geobot_plataforma_backend.core.database import check_db_connection

# Routers
from src.geobot_plataforma_backend.api.routers import (
    auth_router,
    denuncia_router,
    fiscalizacao_router,
    metadata_router,
)


tags_metadata = [
    {
        'name': 'auth',
        'description': 'Endpoints de autenticação e gerenciamento de sessões de usuários.'
    },
    {
        'name': 'denuncias',
        'description': 'Operações de criação, consulta e atualização de denúncias.'
    },
    {
        'name': 'fiscalizacao',
        'description': 'Fluxo de fiscalização relacionado às denúncias.'
    },
    {
        'name': 'Metadata',
        'description': 'Metadados do sistema (enums, opções, configurações).'
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title='Geobot Plataforma API',
        version='1.0',
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        openapi_url='/swagger.json',
        openapi_tags=tags_metadata,
    )

    # CORS
    if settings.get('cors_enabled', True):
        allowed_origins = settings.get('cors_allow_origins', [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ])
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(allowed_origins),
            allow_credentials=settings.get('cors_allow_credentials', True),
            allow_methods=settings.get('cors_allow_methods', ["*"]),
            allow_headers=settings.get('cors_allow_headers', ["*"]),
        )

    # incluir routers
    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(denuncia_router, prefix="/api")
    app.include_router(fiscalizacao_router, prefix="/api")
    app.include_router(metadata_router)  # Já tem prefix="/api/metadata" no router

    @app.get('/')
    def root():
        return JSONResponse({
            'message': f'Bem-vindo à API {settings.app_name}',
            'version': settings.app_version,
            'status': 'online',
            'environment': settings.current_env,
            'documentation': '/api/docs',
            'swagger_json': '/swagger.json'
        })

    @app.get('/health')
    def health():
        db_status = check_db_connection()
        return JSONResponse({
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected'
        }, status_code=200 if db_status else 503)

    @app.get('/api/v1/')
    def api_info():
        return JSONResponse({
            'api_version': 'v1',
            'swagger_ui': '/api/docs',
            'swagger_json': '/swagger.json',
            'endpoints': {
                'health': '/health',
                'documentation': '/api/docs',
                'auth': {
                    'cadastro': '/api/auth/cadastro',
                    'login': '/api/auth/login',
                    'logout': '/api/auth/logout',
                    'me': '/api/auth/me',
                    'validar_token': '/api/auth/validar-token'
                }
            }
        })

    return app


app = create_app()
