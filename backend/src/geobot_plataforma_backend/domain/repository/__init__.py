"""
Repositórios de acesso a dados
"""
from .denuncia_repository import DenunciaRepository
from .usuario_repository import UsuarioRepository

__all__ = [
    "DenunciaRepository",
    "UsuarioRepository",
]
