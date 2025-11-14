"""Router (FastAPI) para rotas de fiscalização"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.core.database import get_db
from src.geobot_plataforma_backend.domain.entity.enums import StatusFiscalizacao
from src.geobot_plataforma_backend.domain.service.fiscalizacao_service import (
    FiscalizacaoService,
    AutorizacaoError,
)
from src.geobot_plataforma_backend.security.dependencies import get_current_user

router = APIRouter(prefix='/fiscalizacao', tags=['fiscalizacao'])


class FiscalizacaoCreatePayload(BaseModel):
    complaint_id: int
    data_conclusao_prevista: Optional[str] = None
    observacoes: Optional[str] = None
    fiscais_ids: Optional[List[int]] = None  # Lista de IDs de fiscais a atribuir


class FiscalizacaoAdicionarFiscalPayload(BaseModel):
    fiscal_id: int
    papel: str = "auxiliar"  # "responsavel" ou "auxiliar"


class FiscalizacaoRemoverFiscalPayload(BaseModel):
    fiscal_id: int


class StatusUpdatePayload(BaseModel):
    status: StatusFiscalizacao


def _to_dict(f):
    """Converte fiscalização para dict com suporte a múltiplos fiscais"""
    # Obter todos os fiscais com seus papéis
    fiscais_data = []
    for atribuicao in f.fiscais_atribuidos:
        fiscais_data.append({
            'id': atribuicao.usuario_id,
            'nome': atribuicao.usuario.nome if atribuicao.usuario else None,
            'email': atribuicao.usuario.email if atribuicao.usuario else None,
            'papel': atribuicao.papel,
            'data_atribuicao': atribuicao.data_atribuicao.isoformat() if atribuicao.data_atribuicao else None
        })
    
    # Encontrar o fiscal responsável (para compatibilidade com frontend antigo)
    fiscal_responsavel_id = None
    for atribuicao in f.fiscais_atribuidos:
        if atribuicao.papel == "responsavel":
            fiscal_responsavel_id = atribuicao.usuario_id
            break
    
    return {
        'id': f.id,
        'uuid': str(f.uuid),
        'complaint_id': f.denuncia_id,  # Frontend espera complaint_id
        'fiscal_responsavel_id': fiscal_responsavel_id,  # DEPRECATED: Mantido para compatibilidade
        'fiscais': fiscais_data,  # NOVO: Array com todos os fiscais e seus papéis
        'codigo': f.codigo,
        'status_fiscalizacao': f.status.value if hasattr(f.status, 'value') else f.status,  # Frontend espera status_fiscalizacao
        'data_inicio': f.data_inicializacao.isoformat() if f.data_inicializacao else None,  # Frontend espera data_inicio
        'data_conclusao_prevista': None,  # Não temos este campo na entidade atualmente
        'data_conclusao_efetiva': f.data_conclusao.isoformat() if f.data_conclusao else None,  # Frontend espera data_conclusao_efetiva
        'observacoes': f.observacoes,
        'data_criacao': f.created_at.isoformat() if f.created_at else None,  # Frontend espera data_criacao
        'data_atualizacao': f.updated_at.isoformat() if f.updated_at else None,  # Frontend espera data_atualizacao
    }


def _value_error_to_status(err: ValueError) -> int:
    mensagem = str(err).lower()
    if "não encontrada" in mensagem or "nao encontrada" in mensagem:
        return status.HTTP_404_NOT_FOUND
    return status.HTTP_400_BAD_REQUEST


@router.post('/', status_code=status.HTTP_201_CREATED)
def criar_fiscalizacao(
    payload: FiscalizacaoCreatePayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria nova fiscalização com múltiplos fiscais.
    Se fiscais_ids não for fornecido, atribui ao usuário atual como fiscal responsável.
    """
    service = FiscalizacaoService(db)
    try:
        fiscalizacao = service.criar_fiscalizacao(
            denuncia_id=payload.complaint_id,
            observacoes=payload.observacoes,
            usuario_id=current_user.id,
            fiscais_ids=payload.fiscais_ids  # NOVO: Aceita lista de fiscais
        )
        return _to_dict(fiscalizacao)
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar fiscalização") from err


@router.get('/', response_model=List[dict])
def listar_fiscalizacoes(
    status_filter: Optional[StatusFiscalizacao] = None,
    fiscal_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista fiscalizações com filtros."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacoes = service.listar_fiscalizacoes(
            usuario_id=current_user.id,
            status_filter=status_filter,
            fiscal_id_filter=fiscal_id,
            limit=limit,
            offset=offset
        )
        return [_to_dict(f) for f in fiscalizacoes]
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar fiscalizações") from err


@router.get('/minhas', response_model=List[dict])
def listar_minhas_fiscalizacoes(
    status_filter: Optional[StatusFiscalizacao] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista fiscalizações do fiscal autenticado."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacoes = service.listar_minhas_fiscalizacoes(
            usuario_id=current_user.id,
            status_filter=status_filter
        )
        return [_to_dict(f) for f in fiscalizacoes]
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar minhas fiscalizações") from err


@router.get('/{id}')
def obter_fiscalizacao(
    id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca uma fiscalização por ID."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacao = service.buscar_fiscalizacao(id, current_user.id)
        return _to_dict(fiscalizacao)
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar fiscalização") from err


@router.post('/{id}/fiscais')
def adicionar_fiscal(
    id: int,
    payload: FiscalizacaoAdicionarFiscalPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adiciona um fiscal a uma fiscalização existente."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacao = service.adicionar_fiscal(
            fiscalizacao_id=id,
            novo_fiscal_id=payload.fiscal_id,
            usuario_id=current_user.id,
            papel=payload.papel
        )
        return _to_dict(fiscalizacao)
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao adicionar fiscal") from err


@router.delete('/{id}/fiscais/{fiscal_id}')
def remover_fiscal(
    id: int,
    fiscal_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um fiscal de uma fiscalização."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacao = service.remover_fiscal(
            fiscalizacao_id=id,
            fiscal_id=fiscal_id,
            usuario_id=current_user.id
        )
        return _to_dict(fiscalizacao)
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao remover fiscal") from err


@router.patch('/{id}/status')
def atualizar_status_fiscalizacao(
    id: int,
    payload: StatusUpdatePayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza o status de uma fiscalização."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacao = service.atualizar_status(id, payload.status, current_user.id)
        return _to_dict(fiscalizacao)
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar status") from err


@router.get('/{id}/historico')
def obter_historico(id: int):
    """Obtém o histórico de uma fiscalização (não implementado)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail='Histórico não implementado')
