"""
Controller para rotas de autenticação com Swagger/OpenAPI
"""
from flask import request
from flask_restx import Namespace, Resource, fields

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

# Criar namespace para autenticação
auth_ns = Namespace('auth', description='Operações de autenticação')

# Modelos para Swagger
cadastro_model = auth_ns.model('UsuarioCadastro', {
    'cpf': fields.String(required=True, description='CPF com 11 dígitos', example='12345678901'),
    'nome': fields.String(required=True, description='Nome completo do usuário', example='João Silva'),
    'email': fields.String(required=True, description='Email válido', example='joao@exemplo.com'),
    'senha': fields.String(required=True, description='Senha forte (min 8 caracteres, maiúsculas, minúsculas, números e especiais)', example='SenhaForte@123')
})

login_model = auth_ns.model('UsuarioLogin', {
    'email': fields.String(required=True, description='Email do usuário', example='joao@exemplo.com'),
    'senha': fields.String(required=True, description='Senha do usuário', example='SenhaForte@123')
})

usuario_response_model = auth_ns.model('UsuarioResponse', {
    'id': fields.Integer(description='ID do usuário'),
    'uuid': fields.String(description='UUID do usuário'),
    'cpf': fields.String(description='CPF do usuário'),
    'nome': fields.String(description='Nome do usuário'),
    'email': fields.String(description='Email do usuário'),
    'ativo': fields.Boolean(description='Status da conta'),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização')
})

login_response_model = auth_ns.model('LoginResponse', {
    'mensagem': fields.String(description='Mensagem de sucesso'),
    'access_token': fields.String(description='Token JWT'),
    'token_type': fields.String(description='Tipo do token', example='Bearer'),
    'expires_in': fields.Integer(description='Tempo de expiração em segundos'),
    'usuario': fields.Nested(usuario_response_model, description='Dados do usuário')
})

cadastro_response_model = auth_ns.model('CadastroResponse', {
    'mensagem': fields.String(description='Mensagem de sucesso'),
    'usuario': fields.Nested(usuario_response_model, description='Dados do usuário cadastrado')
})

erro_model = auth_ns.model('Erro', {
    'erro': fields.String(description='Tipo do erro'),
    'mensagem': fields.String(description='Descrição do erro')
})

token_validation_model = auth_ns.model('TokenValidation', {
    'valido': fields.Boolean(description='Se o token é válido'),
    'mensagem': fields.String(description='Mensagem de status'),
    'usuario': fields.Nested(usuario_response_model, description='Dados do usuário')
})

logout_response_model = auth_ns.model('LogoutResponse', {
    'mensagem': fields.String(description='Mensagem de sucesso'),
    'usuario': fields.String(description='Nome do usuário')
})


@auth_ns.route('/cadastro')
class Cadastro(Resource):
    """Endpoint para cadastro de usuários"""
    
    @auth_ns.doc('cadastrar_usuario',
                 responses={
                     201: ('Usuário cadastrado com sucesso', cadastro_response_model),
                     400: ('Erro de validação', erro_model),
                     500: ('Erro interno do servidor', erro_model)
                 })
    @auth_ns.expect(cadastro_model, validate=True)
    @auth_ns.marshal_with(cadastro_response_model, code=201)
    def post(self):
        """
        Cadastra um novo usuário no sistema
        
        Requisitos da senha:
        - Mínimo 8 caracteres
        - Pelo menos 1 letra maiúscula
        - Pelo menos 1 letra minúscula
        - Pelo menos 1 número
        - Pelo menos 1 caractere especial
        
        Validações:
        - CPF deve ter 11 dígitos
        - Email deve ser válido e único
        - CPF deve ser único
        """
        try:
            dados_json = request.json
            
            # Validar campos obrigatórios
            campos_obrigatorios = ['cpf', 'nome', 'email', 'senha']
            campos_faltantes = [campo for campo in campos_obrigatorios if campo not in dados_json]
            
            if campos_faltantes:
                auth_ns.abort(400, f'Campos obrigatórios faltando: {", ".join(campos_faltantes)}')
            
            # Criar DTO
            try:
                dados_dto = UsuarioCadastroDTO(
                    cpf=dados_json['cpf'],
                    nome=dados_json['nome'],
                    email=dados_json['email'],
                    senha=dados_json['senha']
                )
            except ValueError as e:
                auth_ns.abort(400, str(e))
            
            # Criar usuário
            db = SessionLocal()
            try:
                auth_service = AuthService(db)
                usuario_criado = auth_service.cadastrar_usuario(dados_dto)
                
                return {
                    'mensagem': 'Usuário cadastrado com sucesso',
                    'usuario': usuario_criado.to_dict()
                }, 201
                
            finally:
                db.close()
        
        except ValueError as e:
            auth_ns.abort(400, str(e))
        
        except Exception as e:
            auth_ns.abort(500, 'Ocorreu um erro ao processar sua solicitação')


@auth_ns.route('/login')
class Login(Resource):
    """Endpoint para autenticação de usuários"""
    
    @auth_ns.doc('login_usuario',
                 responses={
                     200: ('Login realizado com sucesso', login_response_model),
                     400: ('Erro de validação', erro_model),
                     401: ('Credenciais inválidas', erro_model),
                     500: ('Erro interno do servidor', erro_model)
                 })
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.marshal_with(login_response_model)
    def post(self):
        """
        Autentica um usuário e retorna um token JWT
        
        Proteção contra brute force:
        - Máximo de 5 tentativas de login
        - Bloqueio temporário de 30 minutos após 5 falhas
        - Contador resetado após login bem-sucedido
        
        O token JWT expira em 60 minutos (configurável).
        """
        try:
            dados_json = request.json
            
            # Validar campos obrigatórios
            if 'email' not in dados_json or 'senha' not in dados_json:
                auth_ns.abort(400, 'Email e senha são obrigatórios')
            
            # Criar DTO
            try:
                dados_dto = UsuarioLoginDTO(
                    email=dados_json['email'],
                    senha=dados_json['senha']
                )
            except ValueError as e:
                auth_ns.abort(400, str(e))
            
            # Autenticar usuário
            db = SessionLocal()
            try:
                auth_service = AuthService(db)
                resultado = auth_service.autenticar(dados_dto)
                
                return {
                    'mensagem': 'Login realizado com sucesso',
                    **resultado.to_dict()
                }, 200
                
            finally:
                db.close()
        
        except ValueError as e:
            auth_ns.abort(401, str(e))
        
        except Exception as e:
            auth_ns.abort(500, 'Ocorreu um erro ao processar sua solicitação')


@auth_ns.route('/logout')
class Logout(Resource):
    """Endpoint para logout de usuários"""
    
    @auth_ns.doc('logout_usuario',
                 security='Bearer',
                 responses={
                     200: ('Logout realizado com sucesso', logout_response_model),
                     401: ('Não autenticado', erro_model),
                     500: ('Erro interno do servidor', erro_model)
                 })
    @auth_ns.marshal_with(logout_response_model)
    @token_required
    def post(self):
        """
        Realiza o logout do usuário autenticado
        
        Com JWT stateless, o logout é feito principalmente no cliente,
        removendo o token. Esta rota serve para confirmar a ação e pode ser
        usada para invalidar o token em uma blacklist futura.
        
        Requer header: Authorization: Bearer <token>
        """
        try:
            usuario_atual = get_usuario_atual()
            
            return {
                'mensagem': 'Logout realizado com sucesso',
                'usuario': usuario_atual['nome']
            }, 200
        
        except Exception as e:
            auth_ns.abort(500, 'Ocorreu um erro ao processar sua solicitação')


@auth_ns.route('/me')
class UsuarioAtual(Resource):
    """Endpoint para obter dados do usuário autenticado"""
    
    @auth_ns.doc('obter_usuario_atual',
                 security='Bearer',
                 responses={
                     200: ('Dados do usuário', usuario_response_model),
                     401: ('Não autenticado', erro_model),
                     500: ('Erro interno do servidor', erro_model)
                 })
    @auth_ns.marshal_with(usuario_response_model)
    @token_required
    def get(self):
        """
        Retorna os dados do usuário autenticado
        
        Requer header: Authorization: Bearer <token>
        """
        try:
            usuario_atual = get_usuario_atual()
            return usuario_atual, 200
        
        except Exception as e:
            auth_ns.abort(500, 'Ocorreu um erro ao processar sua solicitação')


@auth_ns.route('/validar-token')
class ValidarToken(Resource):
    """Endpoint para validar token JWT"""
    
    @auth_ns.doc('validar_token',
                 security='Bearer',
                 responses={
                     200: ('Token válido', token_validation_model),
                     401: ('Token inválido ou expirado', erro_model),
                     500: ('Erro interno do servidor', erro_model)
                 })
    @auth_ns.marshal_with(token_validation_model)
    @token_required
    def get(self):
        """
        Valida se o token JWT ainda é válido
        
        Requer header: Authorization: Bearer <token>
        """
        try:
            usuario_atual = get_usuario_atual()
            
            return {
                'valido': True,
                'mensagem': 'Token válido',
                'usuario': usuario_atual
            }, 200
        
        except Exception as e:
            auth_ns.abort(500, 'Ocorreu um erro ao processar sua solicitação')

