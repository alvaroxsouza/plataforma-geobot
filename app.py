from flask import Flask, jsonify

# Importar configurações e banco de dados
from src.geobot_plataforma_backend.core.config import settings
from src.geobot_plataforma_backend.core.database import check_db_connection, DATABASE_URL
from src.geobot_plataforma_backend.core.migrations import run_migrations, check_pending_migrations

# Importar controllers
from src.geobot_plataforma_backend.api.controller.auth_controller import auth_bp

app = Flask(__name__)

# Configurações usando Dynaconf
app.config['SECRET_KEY'] = settings.secret_key
app.config['DATABASE_URL'] = DATABASE_URL
app.config['DEBUG'] = settings.debug

# Registrar blueprints
app.register_blueprint(auth_bp)

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
        'environment': settings.current_env
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
        'endpoints': {
            'health': '/health',
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

    app.run(
        debug=settings.debug,
        host=settings.host,
        port=settings.port
    )

