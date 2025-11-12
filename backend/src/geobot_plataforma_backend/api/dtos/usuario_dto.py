"""
DTOs para operações de usuário
"""
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, EmailStr, validator, Field


class UsuarioCadastroDTO(BaseModel):
    """DTO para cadastro de novo usuário"""
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF com exatamente 11 dígitos numéricos")
    nome: str = Field(..., min_length=3, description="Nome deve ter pelo menos 3 caracteres")
    email: EmailStr
    senha: str = Field(..., min_length=8, description="Senha deve ter pelo menos 8 caracteres")

    @validator('cpf')
    def validar_cpf(cls, v: str) -> str:
        """Valida se o CPF tem exatamente 11 dígitos numéricos"""
        if not v or len(v) != 11 or not v.isdigit():
            raise ValueError("CPF deve conter exatamente 11 dígitos numéricos")
        return v

    @validator('nome')
    def validar_nome(cls, v: str) -> str:
        """Valida se o nome tem pelo menos 3 caracteres"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Nome deve ter pelo menos 3 caracteres")
        return v

    @validator('senha')
    def validar_senha(cls, v: str) -> str:
        """Valida se a senha tem pelo menos 8 caracteres"""
        if not v or len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        return v

    class Config:
        from_attributes = True


class UsuarioLoginDTO(BaseModel):
    """DTO para login de usuário"""
    email: EmailStr
    senha: str = Field(..., min_length=1, description="Senha é obrigatória")

    @validator('senha')
    def validar_senha(cls, v: str) -> str:
        """Valida se a senha foi fornecida"""
        if not v:
            raise ValueError("Senha é obrigatória")
        return v

    class Config:
        from_attributes = True


class GrupoSimplificadoDTO(BaseModel):
    """DTO simplificado para grupo de usuário"""
    id: int
    nome: str
    descricao: Optional[str] = None
    
    class Config:
        from_attributes = True


class UsuarioResponseDTO(BaseModel):
    """DTO para resposta com dados do usuário (sem informações sensíveis)"""
    id: int
    uuid: str
    cpf: str
    nome: str
    email: str
    ativo: bool
    grupos: List[GrupoSimplificadoDTO] = []
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_entity(cls, usuario):
        """Cria um DTO a partir da entidade Usuario"""
        # Extrair grupos do relacionamento
        grupos_list = []
        if hasattr(usuario, 'grupos') and usuario.grupos:
            for usuario_grupo in usuario.grupos:
                if hasattr(usuario_grupo, 'grupo') and usuario_grupo.grupo:
                    grupos_list.append(GrupoSimplificadoDTO(
                        id=usuario_grupo.grupo.id,
                        nome=usuario_grupo.grupo.nome,
                        descricao=usuario_grupo.grupo.descricao
                    ))
        
        return cls(
            id=usuario.id,
            uuid=str(usuario.uuid),
            cpf=usuario.cpf,
            nome=usuario.nome,
            email=usuario.email,
            ativo=usuario.ativo,
            grupos=grupos_list,
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
            'grupos': [{'id': g.id, 'nome': g.nome, 'descricao': g.descricao} for g in self.grupos],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LoginResponseDTO(BaseModel):
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

    class Config:
        from_attributes = True


class TokenPayloadDTO(BaseModel):
    """DTO para o payload do token JWT"""
    sub: str  # subject (user uuid)
    usuario_id: int
    email: str
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp
    jti: Optional[str] = None  # JWT ID (para controle de revogação)

    class Config:
        from_attributes = True

