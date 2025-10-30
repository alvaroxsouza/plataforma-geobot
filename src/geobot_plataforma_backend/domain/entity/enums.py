"""
Enums do sistema
"""
import enum


class StatusDenuncia(str, enum.Enum):
    """Status de uma denúncia"""
    PENDENTE = "pendente"
    EM_ANALISE = "em_analise"
    EM_FISCALIZACAO = "em_fiscalizacao"
    CONCLUIDA = "concluida"
    ARQUIVADA = "arquivada"
    CANCELADA = "cancelada"


class CategoriaDenuncia(str, enum.Enum):
    """Categoria de uma denúncia"""
    AMBIENTAL = "ambiental"
    SANITARIA = "sanitaria"
    CONSTRUCAO_IRREGULAR = "construcao_irregular"
    POLUICAO_SONORA = "poluicao_sonora"
    OUTROS = "outros"


class Prioridade(str, enum.Enum):
    """Prioridade de uma denúncia"""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class StatusFiscalizacao(str, enum.Enum):
    """Status de uma fiscalização"""
    AGUARDANDO = "aguardando"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class TipoAnalise(str, enum.Enum):
    """Tipo de análise de IA"""
    IMAGEM = "imagem"
    TEXTO = "texto"
    RELATORIO = "relatorio"
    VIDEO = "video"

