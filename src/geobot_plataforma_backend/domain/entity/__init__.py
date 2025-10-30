"""
Entidades do domínio
"""
from .models import (
    Usuario, Grupo, Role, UsuarioGrupo, GrupoRole,
    Endereco, Denuncia, Fiscalizacao, Analise, Arquivo,
    ArquivoDenuncia, ArquivoFiscalizacao, ArquivoAnalise
)
from .enums import (
    StatusDenuncia, CategoriaDenuncia, Prioridade,
    StatusFiscalizacao, TipoAnalise
)

__all__ = [
    # Models
    "Usuario",
    "Grupo",
    "Role",
    "UsuarioGrupo",
    "GrupoRole",
    "Endereco",
    "Denuncia",
    "Fiscalizacao",
    "Analise",
    "Arquivo",
    "ArquivoDenuncia",
    "ArquivoFiscalizacao",
    "ArquivoAnalise",
    # Enums
    "StatusDenuncia",
    "CategoriaDenuncia",
    "Prioridade",
    "StatusFiscalizacao",
    "TipoAnalise",
]

