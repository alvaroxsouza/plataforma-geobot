"""
Serviço para gerenciamento de tokens JWT
"""
import jwt
import uuid as uuid_lib
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.geobot_plataforma_backend.core.config import settings
from src.geobot_plataforma_backend.api.dtos.usuario_dto import TokenPayloadDTO


class JWTService:
    """Serviço para criação e validação de tokens JWT"""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.get('jwt_algorithm', 'HS256')
        self.expiration_minutes = settings.get('jwt_expiration_minutes', 60)

    def gerar_token(self, usuario_id: int, usuario_uuid: str, email: str) -> tuple[str, int]:
        """
        Gera um token JWT para o usuário
        
        Args:
            usuario_id: ID do usuário
            usuario_uuid: UUID do usuário
            email: Email do usuário
            
        Returns:
            Tupla com (token, timestamp de expiração)
        """
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=self.expiration_minutes)
        
        payload = {
            'sub': str(usuario_uuid),  # subject (identificador único do usuário)
            'usuario_id': usuario_id,
            'email': email,
            'iat': int(now.timestamp()),  # issued at
            'exp': int(exp.timestamp()),  # expiration
            'jti': str(uuid_lib.uuid4())  # JWT ID único
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, int(exp.timestamp())

    def validar_token(self, token: str) -> Optional[TokenPayloadDTO]:
        """
        Valida e decodifica um token JWT
        
        Args:
            token: Token JWT a ser validado
            
        Returns:
            TokenPayloadDTO com os dados do token ou None se inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            return TokenPayloadDTO(
                sub=payload['sub'],
                usuario_id=payload['usuario_id'],
                email=payload['email'],
                exp=payload['exp'],
                iat=payload['iat'],
                jti=payload.get('jti')
            )
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None
        except Exception:
            # Qualquer outro erro
            return None

    def extrair_token_do_header(self, authorization_header: Optional[str]) -> Optional[str]:
        """
        Extrai o token do header Authorization
        
        Args:
            authorization_header: Header Authorization (ex: "Bearer token...")
            
        Returns:
            Token extraído ou None
        """
        if not authorization_header:
            return None
        
        parts = authorization_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]

    def verificar_expiracao(self, exp_timestamp: int) -> bool:
        """
        Verifica se o token está expirado
        
        Args:
            exp_timestamp: Timestamp de expiração do token
            
        Returns:
            True se expirado, False caso contrário
        """
        now = datetime.now(timezone.utc)
        exp_date = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        return now > exp_date

    def obter_tempo_restante(self, exp_timestamp: int) -> int:
        """
        Calcula o tempo restante até a expiração do token
        
        Args:
            exp_timestamp: Timestamp de expiração do token
            
        Returns:
            Tempo restante em segundos (0 se já expirado)
        """
        now = datetime.now(timezone.utc)
        exp_date = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        delta = exp_date - now
        
        return max(0, int(delta.total_seconds()))

