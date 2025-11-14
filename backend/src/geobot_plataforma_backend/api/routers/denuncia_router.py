"""Router (FastAPI) para rotas de denúncia

Este módulo contém os endpoints para operações de criação, consulta e 
atualização de denúncias no sistema Geobot Plataforma.

Endpoints disponíveis:
- GET /denuncias/: Lista denúncias do usuário ou todas (admin/fiscal)
- POST /denuncias/: Cria uma nova denúncia
- GET /denuncias/{id}: Busca uma denúncia específica
- PATCH /denuncias/{id}: Atualiza uma denúncia
- DELETE /denuncias/{id}: Deleta uma denúncia
- PATCH /denuncias/{id}/status: Atualiza o status de uma denúncia (admin/fiscal)
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
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
    """Payload para criação de denúncia conforme especificação Swagger
    
    Campos obrigatórios:
    - categoria: Categoria da denúncia
    - prioridade: Prioridade da denúncia
    - observacao: Descrição detalhada do problema
    - logradouro: Nome da rua/avenida
    - bairro: Nome do bairro
    - cidade: Nome da cidade
    - estado: Sigla do estado (UF)
    - cep: Código postal
    """
    categoria: CategoriaDenuncia = Field(..., description="Categoria da denúncia")
    prioridade: Prioridade = Field(..., description="Prioridade da denúncia")
    observacao: str = Field(..., description="Descrição detalhada do problema")
    logradouro: str = Field(..., description="Nome da rua/avenida")
    numero: Optional[str] = Field(None, description="Número do endereço")
    complemento: Optional[str] = Field(None, description="Complemento do endereço")
    bairro: str = Field(..., description="Nome do bairro")
    cidade: str = Field(..., description="Nome da cidade")
    estado: str = Field(..., description="Sigla do estado (UF)")
    cep: str = Field(..., description="Código postal")
    latitude: Optional[float] = Field(None, description="Coordenada geográfica (latitude)")
    longitude: Optional[float] = Field(None, description="Coordenada geográfica (longitude)")


class DenunciaAtualizarPayload(BaseModel):
    """Payload para atualização de denúncia conforme especificação Swagger
    
    Todos os campos são opcionais, permitindo atualização parcial.
    """
    observacao: Optional[str] = Field(None, description="Nova descrição do problema")
    prioridade: Optional[Prioridade] = Field(None, description="Nova prioridade da denúncia")


class StatusUpdatePayload(BaseModel):
    """Payload para atualização de status da denúncia
    
    Apenas admin e fiscal podem alterar o status.
    """
    status: StatusDenuncia = Field(..., description="Novo status da denúncia")


def _value_error_to_status(err: ValueError) -> int:
    mensagem = str(err).lower()
    if "não encontrada" in mensagem or "nao encontrada" in mensagem:
        return status.HTTP_404_NOT_FOUND
    return status.HTTP_400_BAD_REQUEST


@router.get(
    "/",
    summary="Listar Denuncias",
    description="Lista denúncias do usuário ou todas (para admin/fiscal) com filtros.",
    operation_id="listar_denuncias_api_denuncias__get",
)
def listar_denuncias(
    status_filter: Optional[StatusDenuncia] = Query(None, alias="status", description="Filtrar por status"),
    categoria_filter: Optional[CategoriaDenuncia] = Query(None, alias="categoria", description="Filtrar por categoria"),
    todas: bool = Query(False, description="Se true, lista todas as denúncias (apenas admin/fiscal)"),
    limit: int = Query(50, ge=1, le=10000, description="Quantidade de registros por página"),
    offset: int = Query(0, ge=0, description="Posição inicial (para paginação)"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista denúncias do usuário ou todas (para admin/fiscal) com paginação e filtros."""
    service = DenunciaService(db)
    try:
        if todas:
            denuncias = service.listar_todas_denuncias(current_user.id, status_filter, limit, offset, categoria_filter)
            total = service.contar_total_denuncias(current_user.id, status_filter, todas=True, categoria_filter=categoria_filter)
        else:
            denuncias = service.listar_minhas_denuncias(current_user.id, status_filter, limit, offset, categoria_filter)
            total = service.contar_total_denuncias(current_user.id, status_filter, todas=False, categoria_filter=categoria_filter)
        
        return {
            "data": [denuncia.to_dict() for denuncia in denuncias],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total,
                "has_prev": offset > 0
            }
        }
    except AutorizacaoError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:  # pragma: no cover - cobertura defensiva
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar denúncias") from err


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Criar Denuncia",
    description="Cria uma nova denúncia.",
    operation_id="criar_denuncia_api_denuncias__post",
)
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


@router.get(
    "/{denuncia_id}",
    summary="Obter Denuncia",
    description="Busca uma denúncia por ID.",
    operation_id="obter_denuncia_api_denuncias__denuncia_id__get",
)
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


@router.patch(
    "/{denuncia_id}",
    summary="Atualizar Denuncia",
    description="Atualiza uma denúncia (apenas criador e status pendente).",
    operation_id="atualizar_denuncia_api_denuncias__denuncia_id__patch",
)
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


@router.delete(
    "/{denuncia_id}",
    status_code=status.HTTP_200_OK,
    summary="Deletar Denuncia",
    description="Deleta uma denúncia (apenas criador e status pendente).",
    operation_id="deletar_denuncia_api_denuncias__denuncia_id__delete",
)
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


@router.patch(
    "/{denuncia_id}/status",
    summary="Atualizar Status",
    description="Atualiza o status de uma denúncia (apenas admin/fiscal).",
    operation_id="atualizar_status_api_denuncias__denuncia_id__status_patch",
)
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
