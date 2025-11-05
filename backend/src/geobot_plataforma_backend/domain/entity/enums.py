"""
Enums do sistema
"""
import enum


class StatusDenuncia(str, enum.Enum):
    """Status de uma denúncia
    
    Valores possíveis:
    - pendente: Denúncia criada, aguardando análise
    - em_analise: Denúncia sendo analisada pela equipe
    - em_fiscalizacao: Denúncia em processo de fiscalização
    - concluida: Denúncia resolvida com sucesso
    - arquivada: Denúncia arquivada
    - cancelada: Denúncia cancelada pelo usuário
    """
    PENDENTE = "pendente"
    EM_ANALISE = "em_analise"
    EM_FISCALIZACAO = "em_fiscalizacao"
    CONCLUIDA = "concluida"
    ARQUIVADA = "arquivada"
    CANCELADA = "cancelada"


class CategoriaDenuncia(str, enum.Enum):
    """Categoria de uma denúncia
    
    Valores possíveis:
    - calcada: Problemas em calçadas (buracos, irregularidades, etc.)
    - rua: Problemas em ruas e vias públicas (asfalto, buracos, etc.)
    - ciclovia: Problemas em ciclovias (obstruções, má conservação, etc.)
    - semaforo: Problemas com semáforos (defeitos, mau funcionamento, etc.)
    - sinalizacao: Problemas com sinalização de trânsito
    - iluminacao: Problemas com iluminação pública (postes, lâmpadas, etc.)
    - lixo_entulho: Problemas com lixo e entulho (acúmulo, descarte irregular, etc.)
    - poluicao: Problemas de poluição (ar, água, visual, etc.)
    - barulho: Poluição sonora e barulho excessivo
    - outros: Outras categorias não especificadas
    """
    CALCADA = "calcada"
    RUA = "rua"
    CICLOVIA = "ciclovia"
    SEMAFORO = "semaforo"
    SINALIZACAO = "sinalizacao"
    ILUMINACAO = "iluminacao"
    LIXO_ENTULHO = "lixo_entulho"
    POLUICAO = "poluicao"
    BARULHO = "barulho"
    OUTROS = "outros"


class Prioridade(str, enum.Enum):
    """Prioridade de uma denúncia
    
    Valores possíveis:
    - baixa: Baixa prioridade, sem urgência
    - media: Prioridade média, requer atenção moderada
    - alta: Alta prioridade, requer atenção prioritária
    - urgente: Urgente, requer ação imediata
    """
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class StatusFiscalizacao(str, enum.Enum):
    """Status de uma fiscalização
    
    Valores possíveis:
    - aguardando: Fiscalização criada, aguardando início
    - em_andamento: Fiscalização em andamento
    - concluida: Fiscalização concluída
    - cancelada: Fiscalização cancelada
    """
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

