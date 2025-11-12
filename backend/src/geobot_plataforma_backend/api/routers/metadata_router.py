"""
Router para metadados do sistema (enums, opções, etc.)
Endpoint público para fornecer informações sobre os tipos de dados disponíveis
"""
from fastapi import APIRouter
from typing import Dict, List

from ...domain.entity.enums import (
    StatusDenuncia,
    CategoriaDenuncia,
    Prioridade,
    StatusFiscalizacao,
)

router = APIRouter(
    prefix="/api/metadata",
    tags=["Metadata"],
)


@router.get(
    "/status-denuncia",
    summary="Lista todos os status de denúncia disponíveis",
    description="""
    Retorna todos os status possíveis para uma denúncia com suas labels e descrições.
    
    **Endpoint público** - não requer autenticação
    """,
)
def listar_status_denuncia() -> Dict[str, List[Dict[str, str]]]:
    """Lista todos os status de denúncia com metadados"""
    
    # Mapeamento de labels legíveis
    labels = {
        StatusDenuncia.PENDENTE: "Pendente",
        StatusDenuncia.EM_ANALISE: "Em Análise",
        StatusDenuncia.EM_FISCALIZACAO: "Em Fiscalização",
        StatusDenuncia.CONCLUIDA: "Concluída",
        StatusDenuncia.ARQUIVADA: "Arquivada",
        StatusDenuncia.CANCELADA: "Cancelada",
    }
    
    # Descrições detalhadas
    descricoes = {
        StatusDenuncia.PENDENTE: "Denúncia criada, aguardando análise",
        StatusDenuncia.EM_ANALISE: "Denúncia sendo analisada pela equipe",
        StatusDenuncia.EM_FISCALIZACAO: "Denúncia em processo de fiscalização",
        StatusDenuncia.CONCLUIDA: "Denúncia resolvida com sucesso",
        StatusDenuncia.ARQUIVADA: "Denúncia arquivada",
        StatusDenuncia.CANCELADA: "Denúncia cancelada pelo usuário",
    }
    
    # Cores sugeridas para o frontend
    cores = {
        StatusDenuncia.PENDENTE: "yellow",
        StatusDenuncia.EM_ANALISE: "blue",
        StatusDenuncia.EM_FISCALIZACAO: "purple",
        StatusDenuncia.CONCLUIDA: "green",
        StatusDenuncia.ARQUIVADA: "gray",
        StatusDenuncia.CANCELADA: "red",
    }
    
    return {
        "status": [
            {
                "value": status.value,
                "label": labels[status],
                "descricao": descricoes[status],
                "cor": cores[status],
            }
            for status in StatusDenuncia
        ]
    }


@router.get(
    "/categorias-denuncia",
    summary="Lista todas as categorias de denúncia disponíveis",
    description="""
    Retorna todas as categorias possíveis para uma denúncia com suas labels, descrições e ícones.
    
    **Endpoint público** - não requer autenticação
    """,
)
def listar_categorias_denuncia() -> Dict[str, List[Dict[str, str]]]:
    """Lista todas as categorias de denúncia com metadados"""
    
    # Mapeamento de labels legíveis
    labels = {
        CategoriaDenuncia.CALCADA: "Calçada",
        CategoriaDenuncia.RUA: "Rua",
        CategoriaDenuncia.CICLOVIA: "Ciclovia",
        CategoriaDenuncia.SEMAFORO: "Semáforo",
        CategoriaDenuncia.SINALIZACAO: "Sinalização",
        CategoriaDenuncia.ILUMINACAO: "Iluminação",
        CategoriaDenuncia.LIXO_ENTULHO: "Lixo e Entulho",
        CategoriaDenuncia.POLUICAO: "Poluição",
        CategoriaDenuncia.BARULHO: "Barulho",
        CategoriaDenuncia.OUTROS: "Outros",
    }
    
    # Descrições detalhadas
    descricoes = {
        CategoriaDenuncia.CALCADA: "Problemas em calçadas (buracos, irregularidades, etc.)",
        CategoriaDenuncia.RUA: "Problemas em ruas e vias públicas (asfalto, buracos, etc.)",
        CategoriaDenuncia.CICLOVIA: "Problemas em ciclovias (obstruções, má conservação, etc.)",
        CategoriaDenuncia.SEMAFORO: "Problemas com semáforos (defeitos, mau funcionamento, etc.)",
        CategoriaDenuncia.SINALIZACAO: "Problemas com sinalização de trânsito",
        CategoriaDenuncia.ILUMINACAO: "Problemas com iluminação pública (postes, lâmpadas, etc.)",
        CategoriaDenuncia.LIXO_ENTULHO: "Problemas com lixo e entulho (acúmulo, descarte irregular, etc.)",
        CategoriaDenuncia.POLUICAO: "Problemas de poluição (ar, água, visual, etc.)",
        CategoriaDenuncia.BARULHO: "Poluição sonora e barulho excessivo",
        CategoriaDenuncia.OUTROS: "Outras categorias não especificadas",
    }
    
    # Ícones sugeridos (emojis)
    icones = {
        CategoriaDenuncia.CALCADA: "🚶",
        CategoriaDenuncia.RUA: "🛣️",
        CategoriaDenuncia.CICLOVIA: "🚴",
        CategoriaDenuncia.SEMAFORO: "🚦",
        CategoriaDenuncia.SINALIZACAO: "🚧",
        CategoriaDenuncia.ILUMINACAO: "💡",
        CategoriaDenuncia.LIXO_ENTULHO: "🗑️",
        CategoriaDenuncia.POLUICAO: "🏭",
        CategoriaDenuncia.BARULHO: "🔊",
        CategoriaDenuncia.OUTROS: "📋",
    }
    
    return {
        "categorias": [
            {
                "value": categoria.value,
                "label": labels[categoria],
                "descricao": descricoes[categoria],
                "icone": icones[categoria],
            }
            for categoria in CategoriaDenuncia
        ]
    }


@router.get(
    "/prioridades",
    summary="Lista todas as prioridades disponíveis",
    description="""
    Retorna todas as prioridades possíveis para uma denúncia com suas labels, descrições e cores.
    
    **Endpoint público** - não requer autenticação
    """,
)
def listar_prioridades() -> Dict[str, List[Dict[str, str]]]:
    """Lista todas as prioridades com metadados"""
    
    # Mapeamento de labels legíveis
    labels = {
        Prioridade.BAIXA: "Baixa",
        Prioridade.MEDIA: "Média",
        Prioridade.ALTA: "Alta",
        Prioridade.URGENTE: "Urgente",
    }
    
    # Descrições detalhadas
    descricoes = {
        Prioridade.BAIXA: "Baixa prioridade, sem urgência",
        Prioridade.MEDIA: "Prioridade média, requer atenção moderada",
        Prioridade.ALTA: "Alta prioridade, requer atenção prioritária",
        Prioridade.URGENTE: "Urgente, requer ação imediata",
    }
    
    # Cores sugeridas para o frontend
    cores = {
        Prioridade.BAIXA: "blue",
        Prioridade.MEDIA: "yellow",
        Prioridade.ALTA: "orange",
        Prioridade.URGENTE: "red",
    }
    
    return {
        "prioridades": [
            {
                "value": prioridade.value,
                "label": labels[prioridade],
                "descricao": descricoes[prioridade],
                "cor": cores[prioridade],
            }
            for prioridade in Prioridade
        ]
    }


@router.get(
    "/",
    summary="Retorna todos os metadados do sistema",
    description="""
    Retorna todos os metadados disponíveis (status, categorias, prioridades) em uma única resposta.
    
    Útil para inicialização do frontend e cache de metadados.
    
    **Endpoint público** - não requer autenticação
    """,
)
def listar_todos_metadados() -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """Retorna todos os metadados do sistema"""
    return {
        "status_denuncia": listar_status_denuncia(),
        "categorias_denuncia": listar_categorias_denuncia(),
        "prioridades": listar_prioridades(),
    }
