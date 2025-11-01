"""
Entidades do domínio
"""
# Importar enums primeiro
from .enums import (
    StatusDenuncia, CategoriaDenuncia, Prioridade,
    StatusFiscalizacao, TipoAnalise
)

# Importar modelos individuais
from .usuario import Usuario
from .grupo import Grupo
from .role import Role
from .usuario_grupo import UsuarioGrupo
from .grupo_role import GrupoRole
from .endereco import Endereco
from .denuncia import Denuncia
from .fiscalizacao import Fiscalizacao
from .analise import Analise
from .arquivo import Arquivo
from .arquivo_denuncia import ArquivoDenuncia
from .arquivo_fiscalizacao import ArquivoFiscalizacao
from .arquivo_analise import ArquivoAnalise

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

