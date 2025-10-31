from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS

# Importar configurações e banco de dados
from src.geobot_plataforma_backend.core.config import settings
from src.geobot_plataforma_backend.core.database import check_db_connection, DATABASE_URL
from src.geobot_plataforma_backend.core.migrations import run_migrations, check_pending_migrations

# Importar controllers
from src.geobot_plataforma_backend.api.controller.auth_controller import auth_bp
from src.geobot_plataforma_backend.api.controller.auth_controller_restx import auth_ns

app = Flask(__name__)

# Configurações usando Dynaconf
app.config['SECRET_KEY'] = settings.secret_key
app.config['DATABASE_URL'] = DATABASE_URL
app.config['DEBUG'] = settings.debug
app.config['RESTX_MASK_SWAGGER'] = False  # Desabilitar máscara de campos no Swagger
app.config['RESTX_VALIDATE'] = True  # Habilitar validação automática

# CORS - configurações
if settings.get('cors_enabled', True):
    # Garante que http://localhost:3000 esteja na lista de origens permitidas
    allowed_origins = set(settings.get('cors_allow_origins', [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]))
    allowed_origins.add("http://localhost:3000")

    # Normaliza métodos e headers (evita "*" que não é aceito com credentials)
    default_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    cfg_methods = settings.get('cors_allow_methods', default_methods)
    if isinstance(cfg_methods, (list, tuple)) and any(m == "*" for m in cfg_methods):
        allowed_methods = default_methods
    else:
        allowed_methods = list(cfg_methods) if isinstance(cfg_methods, (list, tuple)) else default_methods

    default_headers = ["Content-Type", "Authorization", "X-Requested-With"]
    cfg_headers = settings.get('cors_allow_headers', default_headers)
    if isinstance(cfg_headers, (list, tuple)) and any(h == "*" for h in cfg_headers):
        allowed_headers = default_headers
    else:
        allowed_headers = list(cfg_headers) if isinstance(cfg_headers, (list, tuple)) else default_headers

    # Aplicar CORS para todas as rotas (inclui /, /health, /api/*, etc.)
    CORS(
        app,
        resources={r"/*": {"origins": list(allowed_origins)}},
        supports_credentials=settings.get('cors_allow_credentials', True),
        methods=allowed_methods,
        allow_headers=allowed_headers
    )

# Configurar Swagger/OpenAPI
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Token JWT. Use o formato: Bearer {token}'
    }
}

api = Api(
    app,
    version='1.0',
    title='Geobot Plataforma API',
    description='''
    API para a plataforma Geobot.
    ''',
    doc='/api/docs',  # Swagger UI
    authorizations=authorizations,
    security='Bearer'
)

# Registrar blueprints antigos (para compatibilidade)
app.register_blueprint(auth_bp)

# Registrar namespaces do Flask-RESTX
api.add_namespace(auth_ns, path='/api/auth')

# Executar migrations automaticamente na inicialização
@app.before_request
def check_and_run_migrations():
    """Verifica e executa migrations pendentes antes da primeira requisição"""
    # Remove o handler após a primeira execução
    if not hasattr(app, '_migrations_checked'):
        try:
            print("🔍 Verificando migrations do banco de dados...")
            has_pending, message = check_pending_migrations()

            if has_pending:
                print(f"⚠️  {message}")
                if settings.get('auto_run_migrations', True):
                    run_migrations()
                else:
                    print("⚠️  Auto-execução de migrations desabilitada. Execute manualmente: python -m src.geobot_plataforma_backend.core.migrations upgrade")
            else:
                print(f"✅ {message}")

        except Exception as e:
            print(f"⚠️  Erro ao verificar migrations: {e}")
            print("⚠️  Continuando sem executar migrations. Verifique a configuração do banco de dados.")

        app._migrations_checked = True


@app.route('/')
def hello_world():
    """Rota de boas-vindas"""
    return jsonify({
        'message': f'Bem-vindo à API {settings.app_name}',
        'version': settings.app_version,
        'status': 'online',
        'environment': settings.current_env,
        'documentation': '/api/docs',
        'swagger_json': '/swagger.json'
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    db_status = check_db_connection()

    return jsonify({
        'status': 'healthy' if db_status else 'unhealthy',
        'database': 'connected' if db_status else 'disconnected'
    }), 200 if db_status else 503


@app.route('/api/v1/')
def api_info():
    """Informações sobre a API"""
    return jsonify({
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


if __name__ == '__main__':
    # Exibir configurações ao iniciar
    print(f"🚀 Iniciando {settings.app_name} v{settings.app_version}")
    print(f"🌍 Ambiente: {settings.current_env}")
    print(f"🗄️  Banco de dados: {settings.db_host}:{settings.db_port}/{settings.db_name}")

    # Verificar conexão com banco ao iniciar
    if check_db_connection():
        print("✓ Conexão com banco de dados estabelecida!")
    else:
        print("✗ Erro ao conectar com banco de dados!")

    # Exibir URL da documentação Swagger
    print(f"\n📚 Documentação Swagger disponível em: http://{settings.host}:{settings.port}/api/docs")
    print(f"📄 Swagger JSON disponível em: http://{settings.host}:{settings.port}/swagger.json\n")

    app.run(
        debug=settings.debug,
        host=settings.host,
        port=settings.port
    )
