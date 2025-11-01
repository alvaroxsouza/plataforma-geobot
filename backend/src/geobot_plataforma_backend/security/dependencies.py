from typing import Optional

from fastapi import Header, HTTPException, status

from src.geobot_plataforma_backend.security.service.jwt_service import JWTService
from src.geobot_plataforma_backend.core.database import SessionLocal
from src.geobot_plataforma_backend.domain.repository.usuario_repository import UsuarioRepository


def _extract_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    jwt_service = JWTService()
    return jwt_service.extrair_token_do_header(authorization)


def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency que valida o token e retorna o usuário (entidade) ou lança 401."""
    token = _extract_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={'erro': 'Token de autenticação não fornecido', 'mensagem': 'É necessário fornecer um token de autenticação válido no header Authorization'})

    jwt_service = JWTService()
    payload = jwt_service.validar_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={'erro': 'Token inválido ou expirado', 'mensagem': 'O token fornecido é inválido ou está expirado. Faça login novamente'})

    db = SessionLocal()
    try:
        repository = UsuarioRepository(db)
        usuario = repository.buscar_por_id(payload.usuario_id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail={'erro': 'Usuário não encontrado', 'mensagem': 'O usuário associado ao token não foi encontrado'})

        if not usuario.ativo:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail={'erro': 'Usuário inativo', 'mensagem': 'Sua conta está inativa. Entre em contato com o administrador'})

        return usuario
    finally:
        db.close()


def get_optional_current_user(authorization: Optional[str] = Header(None)):
    token = _extract_token(authorization)
    if not token:
        return None

    jwt_service = JWTService()
    payload = jwt_service.validar_token(token)
    if not payload:
        return None

    db = SessionLocal()
    try:
        repository = UsuarioRepository(db)
        usuario = repository.buscar_por_id(payload.usuario_id)
        if usuario and usuario.ativo:
            return usuario
        return None
    finally:
        db.close()
