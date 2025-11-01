"""
Routers da API
"""
from .auth_router import router as auth_router
from .denuncia_router import router as denuncia_router
from .fiscalizacao_router import router as fiscalizacao_router

__all__ = [
    "auth_router",
    "denuncia_router",
    "fiscalizacao_router",
]
