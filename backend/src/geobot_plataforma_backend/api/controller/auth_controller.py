"""
Controller para rotas de autenticação
"""
from flask import Blueprint, request, jsonify

from src.geobot_plataforma_backend.core.database import SessionLocal
from src.geobot_plataforma_backend.domain.service.auth_service import AuthService
from src.geobot_plataforma_backend.api.dtos.usuario_dto import (
    UsuarioCadastroDTO,
    UsuarioLoginDTO
)
from src.geobot_plataforma_backend.security.middleware.auth_middleware import (
    token_required,
    get_usuario_atual
)

# Criar blueprint para rotas de autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    """
    Rota para cadastro de novo usuário
    
    Body (JSON):
    {
        "cpf": "12345678901",
        "nome": "Nome do Usuário",
        "email": "usuario@exemplo.com",
        "senha": "SenhaForte@123"
    }
    
    Returns:
        201: Usuário cadastrado com sucesso
        400: Erro de validação
        500: Erro interno
    """
    try:
        # Obter dados do body
        dados_json = request.get_json()
        
        if not dados_json:
            return jsonify({
                'erro': 'Dados inválidos',
                'mensagem': 'É necessário fornecer os dados do usuário no formato JSON'
            }), 400
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['cpf', 'nome', 'email', 'senha']
        campos_faltantes = [campo for campo in campos_obrigatorios if campo not in dados_json]
        
        if campos_faltantes:
            return jsonify({
                'erro': 'Campos obrigatórios faltando',
                'mensagem': f'Os seguintes campos são obrigatórios: {", ".join(campos_faltantes)}'
            }), 400
        
        # Criar DTO
        try:
            dados_dto = UsuarioCadastroDTO(
                cpf=dados_json['cpf'],
                nome=dados_json['nome'],
                email=dados_json['email'],
                senha=dados_json['senha']
            )
        except ValueError as e:
            return jsonify({
                'erro': 'Erro de validação',
                'mensagem': str(e)
            }), 400
        
        # Criar usuário
        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            usuario_criado = auth_service.cadastrar_usuario(dados_dto)
            
            return jsonify({
                'mensagem': 'Usuário cadastrado com sucesso',
                'usuario': usuario_criado.to_dict()
            }), 201
            
        finally:
            db.close()
    
    except ValueError as e:
        return jsonify({
            'erro': 'Erro de validação',
            'mensagem': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Ocorreu um erro ao processar sua solicitação'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Rota para autenticação de usuário
    
    Body (JSON):
    {
        "email": "usuario@exemplo.com",
        "senha": "SenhaForte@123"
    }
    
    Returns:
        200: Login bem-sucedido com token JWT
        400: Erro de validação
        401: Credenciais inválidas
        500: Erro interno
    """
    try:
        # Obter dados do body
        dados_json = request.get_json()
        
        if not dados_json:
            return jsonify({
                'erro': 'Dados inválidos',
                'mensagem': 'É necessário fornecer email e senha no formato JSON'
            }), 400
        
        # Validar campos obrigatórios
        if 'email' not in dados_json or 'senha' not in dados_json:
            return jsonify({
                'erro': 'Campos obrigatórios faltando',
                'mensagem': 'Email e senha são obrigatórios'
            }), 400
        
        # Criar DTO
        try:
            dados_dto = UsuarioLoginDTO(
                email=dados_json['email'],
                senha=dados_json['senha']
            )
        except ValueError as e:
            return jsonify({
                'erro': 'Erro de validação',
                'mensagem': str(e)
            }), 400
        
        # Autenticar usuário
        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            resultado = auth_service.autenticar(dados_dto)
            
            return jsonify({
                'mensagem': 'Login realizado com sucesso',
                **resultado.to_dict()
            }), 200
            
        finally:
            db.close()
    
    except ValueError as e:
        return jsonify({
            'erro': 'Credenciais inválidas',
            'mensagem': str(e)
        }), 401
    
    except Exception as e:
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Ocorreu um erro ao processar sua solicitação'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Rota para logout do usuário
    
    Nota: Com JWT stateless, o logout é feito principalmente no cliente,
    removendo o token. Esta rota serve para confirmar a ação e pode ser
    usada para invalidar o token em uma blacklist futura.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Logout realizado
        401: Não autenticado
    """
    try:
        usuario_atual = get_usuario_atual()
        
        # Aqui você poderia adicionar o token a uma blacklist
        # Por enquanto, apenas confirmamos o logout
        
        return jsonify({
            'mensagem': 'Logout realizado com sucesso',
            'usuario': usuario_atual['nome']
        }), 200
    
    except Exception as e:
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Ocorreu um erro ao processar sua solicitação'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def obter_usuario_atual():
    """
    Rota para obter dados do usuário autenticado
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Dados do usuário
        401: Não autenticado
    """
    try:
        usuario_atual = get_usuario_atual()
        
        return jsonify({
            'usuario': usuario_atual
        }), 200
    
    except Exception as e:
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Ocorreu um erro ao processar sua solicitação'
        }), 500


@auth_bp.route('/validar-token', methods=['GET'])
@token_required
def validar_token():
    """
    Rota para validar se o token ainda é válido
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Token válido
        401: Token inválido ou expirado
    """
    try:
        usuario_atual = get_usuario_atual()
        
        return jsonify({
            'valido': True,
            'mensagem': 'Token válido',
            'usuario': usuario_atual
        }), 200
    
    except Exception as e:
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Ocorreu um erro ao processar sua solicitação'
        }), 500


# Tratamento de erros específicos do blueprint
@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'erro': 'Rota não encontrada',
        'mensagem': 'A rota solicitada não existe'
    }), 404


@auth_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'erro': 'Método não permitido',
        'mensagem': 'O método HTTP utilizado não é permitido para esta rota'
    }), 405

