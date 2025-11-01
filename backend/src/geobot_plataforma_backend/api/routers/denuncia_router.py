"""Router (FastAPI) para rotas de denúncia"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.core.database import get_db
from src.geobot_plataforma_backend.domain.entity.enums import (
    StatusDenuncia,
    CategoriaDenuncia,
    Prioridade,
)
from src.geobot_plataforma_backend.domain.service.denuncia_service import (
    DenunciaService,
    AutorizacaoError,
)
from src.geobot_plataforma_backend.api.dtos.denuncia_dto import (
    DenunciaCriarDTO,
    DenunciaAtualizarDTO,
)
from src.geobot_plataforma_backend.security.dependencies import get_current_user

router = APIRouter(prefix="/denuncias", tags=["denuncias"])


class DenunciaCriarPayload(BaseModel):
    categoria: CategoriaDenuncia
    prioridade: Prioridade
    observacao: str
    logradouro: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DenunciaAtualizarPayload(BaseModel):
    observacao: Optional[str] = None
    prioridade: Optional[Prioridade] = None


class StatusUpdatePayload(BaseModel):
    status: StatusDenuncia


def _value_error_to_status(err: ValueError) -> int:
    mensagem = str(err).lower()
    if "não encontrada" in mensagem or "nao encontrada" in mensagem:
        return status.HTTP_404_NOT_FOUND
    return status.HTTP_400_BAD_REQUEST


@router.get("/", response_model=List[dict])
def listar_denuncias(
    status_filter: Optional[StatusDenuncia] = Query(None, alias="status"),
    todas: bool = Query(False, description="Se true, lista todas as denúncias (apenas admin/fiscal)"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista denúncias do usuário ou todas (para admin/fiscal)."""
    service = DenunciaService(db)
    try:
        if todas:
            denuncias = service.listar_todas_denuncias(current_user.id, status_filter)
        else:
            denuncias = service.listar_minhas_denuncias(current_user.id, status_filter)
        return [denuncia.to_dict() for denuncia in denuncias]
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:  # pragma: no cover - cobertura defensiva
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar denúncias") from err


@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_denuncia(
    payload: DenunciaCriarPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria uma nova denúncia."""
    service = DenunciaService(db)
    try:
        dto = DenunciaCriarDTO(
            categoria=payload.categoria,
            prioridade=payload.prioridade,
            observacao=payload.observacao,
            logradouro=payload.logradouro,
            numero=payload.numero,
            complemento=payload.complemento,
            bairro=payload.bairro,
            cidade=payload.cidade,
            estado=payload.estado,
            cep=payload.cep,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        denuncia = service.criar_denuncia(dto, current_user.id)
        return denuncia.to_dict()
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:  # pragma: no cover - cobertura defensiva
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar denúncia") from err


@router.get("/{denuncia_id}")
def obter_denuncia(
    denuncia_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Busca uma denúncia por ID."""
    service = DenunciaService(db)
    try:
        denuncia = service.buscar_denuncia(denuncia_id, current_user.id)
        return denuncia.to_dict()
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar denúncia") from err


@router.patch("/{denuncia_id}")
def atualizar_denuncia(
    denuncia_id: int,
    payload: DenunciaAtualizarPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza uma denúncia (apenas criador e status pendente)."""
    service = DenunciaService(db)
    try:
        dto = DenunciaAtualizarDTO(
            observacao=payload.observacao,
            prioridade=payload.prioridade,
        )
        denuncia = service.atualizar_denuncia(denuncia_id, dto, current_user.id)
        return denuncia.to_dict()
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar denúncia") from err


@router.delete("/{denuncia_id}", status_code=status.HTTP_200_OK)
def deletar_denuncia(
    denuncia_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deleta uma denúncia (apenas criador e status pendente)."""
    service = DenunciaService(db)
    try:
        service.deletar_denuncia(denuncia_id, current_user.id)
        return {"mensagem": "Denúncia deletada com sucesso"}
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar denúncia") from err


@router.patch("/{denuncia_id}/status")
def atualizar_status(
    denuncia_id: int,
    payload: StatusUpdatePayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza o status de uma denúncia (apenas admin/fiscal)."""
    service = DenunciaService(db)
    try:
        denuncia = service.atualizar_status_denuncia(
            denuncia_id,
            payload.status,
            current_user.id,
        )
        return denuncia.to_dict()
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar status da denúncia") from err
