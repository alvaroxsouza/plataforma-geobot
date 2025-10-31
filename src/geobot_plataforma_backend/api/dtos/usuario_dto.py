"""
DTOs para operações de usuário
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UsuarioCadastroDTO:
    """DTO para cadastro de novo usuário"""
    cpf: str
    nome: str
    email: str
    senha: str

    def __post_init__(self):
        """Validação básica dos dados"""
        if not self.cpf or len(self.cpf) != 11 or not self.cpf.isdigit():
            raise ValueError("CPF deve conter exatamente 11 dígitos numéricos")
        
        if not self.nome or len(self.nome.strip()) < 3:
            raise ValueError("Nome deve ter pelo menos 3 caracteres")
        
        if not self.email or '@' not in self.email:
            raise ValueError("Email inválido")
        
        if not self.senha or len(self.senha) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")


@dataclass
class UsuarioLoginDTO:
    """DTO para login de usuário"""
    email: str
    senha: str

    def __post_init__(self):
        """Validação básica dos dados"""
        if not self.email or '@' not in self.email:
            raise ValueError("Email inválido")
        
        if not self.senha:
            raise ValueError("Senha é obrigatória")


@dataclass
class UsuarioResponseDTO:
    """DTO para resposta com dados do usuário (sem informações sensíveis)"""
    id: int
    uuid: str
    cpf: str
    nome: str
    email: str
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_entity(cls, usuario):
        """Cria um DTO a partir da entidade Usuario"""
        return cls(
            id=usuario.id,
            uuid=str(usuario.uuid),
            cpf=usuario.cpf,
            nome=usuario.nome,
            email=usuario.email,
            ativo=usuario.ativo,
            created_at=usuario.created_at,
            updated_at=usuario.updated_at
        )

    def to_dict(self):
        """Converte o DTO para dicionário"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'cpf': self.cpf,
            'nome': self.nome,
            'email': self.email,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class LoginResponseDTO:
    """DTO para resposta de login bem-sucedido"""
    access_token: str
    token_type: str
    expires_in: int
    usuario: UsuarioResponseDTO

    def to_dict(self):
        """Converte o DTO para dicionário"""
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in,
            'usuario': self.usuario.to_dict()
        }


@dataclass
class TokenPayloadDTO:
    """DTO para o payload do token JWT"""
    sub: str  # subject (user uuid)
    usuario_id: int
    email: str
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp
    jti: Optional[str] = None  # JWT ID (para controle de revogação)

