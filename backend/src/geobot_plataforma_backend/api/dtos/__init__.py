"""
Exportações dos DTOs da API
"""
from .denuncia_dto import (
    DenunciaCriarDTO,
    DenunciaAtualizarDTO,
    DenunciaResponseDTO,
)
from .usuario_dto import (
    UsuarioCadastroDTO,
    UsuarioLoginDTO,
    UsuarioResponseDTO,
    LoginResponseDTO,
    TokenPayloadDTO,
)

__all__ = [
    # DTOs de Denúncia
    "DenunciaCriarDTO",
    "DenunciaAtualizarDTO",
    "DenunciaResponseDTO",
    # DTOs de Usuário
    "UsuarioCadastroDTO",
    "UsuarioLoginDTO",
    "UsuarioResponseDTO",
    "LoginResponseDTO",
    "TokenPayloadDTO",
]
