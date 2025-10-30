from flask import Flask, jsonify
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Importar configuração do banco de dados
from src.geobot_plataforma_backend.core.database import check_db_connection

app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def hello_world():
    """Rota de boas-vindas"""
    return jsonify({
        'message': 'Bem-vindo à API Geobot Plataforma',
        'version': '0.1.0',
        'status': 'online'
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
            'docs': '/api/v1/docs'
        }
    })


if __name__ == '__main__':
    # Verificar conexão com banco ao iniciar
    if check_db_connection():
        print("✓ Conexão com banco de dados estabelecida!")
    else:
        print("✗ Erro ao conectar com banco de dados!")

    app.run(debug=True, host='0.0.0.0', port=5000)
