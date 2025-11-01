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


class FiscalizacaoAtribuirPayload(BaseModel):
    fiscal_id: int


class StatusUpdatePayload(BaseModel):
    status: StatusFiscalizacao


def _to_dict(f):
    """Converte fiscalização para dict"""
    return {
        'id': f.id,
        'uuid': str(f.uuid),
        'denuncia_id': f.denuncia_id,
        'fiscal_id': f.fiscal_id,
        'codigo': f.codigo,
        'status': f.status.value if hasattr(f.status, 'value') else f.status,
        'data_inicializacao': f.data_inicializacao.isoformat() if f.data_inicializacao else None,
        'data_conclusao': f.data_conclusao.isoformat() if f.data_conclusao else None,
        'observacoes': f.observacoes,
        'created_at': f.created_at.isoformat() if f.created_at else None,
        'updated_at': f.updated_at.isoformat() if f.updated_at else None,
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
    """Cria nova fiscalização. Atribui ao usuário atual como fiscal."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacao = service.criar_fiscalizacao(
            denuncia_id=payload.complaint_id,
            observacoes=payload.observacoes,
            usuario_id=current_user.id
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


@router.patch('/{id}/atribuir')
def atribuir_fiscal(
    id: int,
    payload: FiscalizacaoAtribuirPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atribui um fiscal a uma fiscalização."""
    service = FiscalizacaoService(db)
    try:
        fiscalizacao = service.atribuir_fiscal(id, payload.fiscal_id, current_user.id)
        return _to_dict(fiscalizacao)
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atribuir fiscal") from err


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
