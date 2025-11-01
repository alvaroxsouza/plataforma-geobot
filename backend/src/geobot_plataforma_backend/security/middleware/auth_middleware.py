"""
Decoradores e middlewares para autenticação
"""
from functools import wraps
from flask import request, jsonify, g
from typing import Optional, Callable

from src.geobot_plataforma_backend.security.service.jwt_service import JWTService
from src.geobot_plataforma_backend.core.database import SessionLocal
from src.geobot_plataforma_backend.domain.repository.usuario_repository import UsuarioRepository


def token_required(f: Callable) -> Callable:
    """
    Decorator para proteger rotas que requerem autenticação
    
    Valida o token JWT no header Authorization e adiciona os dados do usuário ao contexto
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Extrair token do header Authorization
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            jwt_service = JWTService()
            token = jwt_service.extrair_token_do_header(auth_header)
        
        if not token:
            return jsonify({
                'erro': 'Token de autenticação não fornecido',
                'mensagem': 'É necessário fornecer um token de autenticação válido no header Authorization'
            }), 401
        
        # Validar token
        jwt_service = JWTService()
        payload = jwt_service.validar_token(token)
        
        if not payload:
            return jsonify({
                'erro': 'Token inválido ou expirado',
                'mensagem': 'O token fornecido é inválido ou está expirado. Faça login novamente'
            }), 401
        
        # Verificar se o usuário existe e está ativo
        db = SessionLocal()
        try:
            repository = UsuarioRepository(db)
            usuario = repository.buscar_por_id(payload.usuario_id)
            
            if not usuario:
                return jsonify({
                    'erro': 'Usuário não encontrado',
                    'mensagem': 'O usuário associado ao token não foi encontrado'
                }), 401
            
            if not usuario.ativo:
                return jsonify({
                    'erro': 'Usuário inativo',
                    'mensagem': 'Sua conta está inativa. Entre em contato com o administrador'
                }), 403
            
            # Adicionar dados do usuário ao contexto da requisição
            g.usuario_atual = usuario
            g.token_payload = payload
            
        finally:
            db.close()
        
        return f(*args, **kwargs)
    
    return decorated


def optional_token(f: Callable) -> Callable:
    """
    Decorator para rotas onde o token é opcional
    
    Se o token for fornecido e válido, adiciona os dados do usuário ao contexto
    Se não for fornecido ou for inválido, continua sem adicionar ao contexto
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Extrair token do header Authorization
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            jwt_service = JWTService()
            token = jwt_service.extrair_token_do_header(auth_header)
        
        if token:
            # Validar token
            jwt_service = JWTService()
            payload = jwt_service.validar_token(token)
            
            if payload:
                # Verificar se o usuário existe e está ativo
                db = SessionLocal()
                try:
                    repository = UsuarioRepository(db)
                    usuario = repository.buscar_por_id(payload.usuario_id)
                    
                    if usuario and usuario.ativo:
                        # Adicionar dados do usuário ao contexto da requisição
                        g.usuario_atual = usuario
                        g.token_payload = payload
                        
                finally:
                    db.close()
        
        return f(*args, **kwargs)
    
    return decorated


def get_usuario_atual() -> Optional[dict]:
    """
    Utilitário para obter o usuário atual do contexto da requisição
    
    Returns:
        Dicionário com dados do usuário ou None se não autenticado
    """
    if hasattr(g, 'usuario_atual'):
        usuario = g.usuario_atual
        return {
            'id': usuario.id,
            'uuid': str(usuario.uuid),
            'cpf': usuario.cpf,
            'nome': usuario.nome,
            'email': usuario.email,
            'ativo': usuario.ativo
        }
    return None

