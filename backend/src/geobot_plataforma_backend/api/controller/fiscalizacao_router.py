"""Router FastAPI para operações de fiscalização

Endpoints implementados (compatíveis com frontend `services/fiscalizacao.ts`):
- POST /fiscalizacao/          -> criar fiscalização (atribui ao usuário atual como fiscal e gera código automático)
- GET  /fiscalizacao/          -> listar fiscalizações (filtros básicos)
- GET  /fiscalizacao/minhas    -> listar fiscalizações do fiscal autenticado
- GET  /fiscalizacao/{id}      -> obter por id
- PATCH /fiscalizacao/{id}/atribuir -> atribuir fiscal (se autorizado)
- GET  /fiscalizacao/{id}/historico -> placeholder (histórico não implementado)

Notas: implementação mínima. TODOs deixados onde as regras de negócios/validações são necessárias.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid

from src.geobot_plataforma_backend.core.database import SessionLocal
from src.geobot_plataforma_backend.domain.entity.fiscalizacao import Fiscalizacao
from src.geobot_plataforma_backend.domain.entity.denuncia import Denuncia
from src.geobot_plataforma_backend.security.dependencies import get_current_user
from src.geobot_plataforma_backend.domain.entity.enums import StatusFiscalizacao

router = APIRouter(prefix='/fiscalizacao', tags=['fiscalizacao'])


class FiscalizacaoCreate(BaseModel):
    complaint_id: int
    data_conclusao_prevista: Optional[str]
    observacoes: Optional[str]


class FiscalizacaoAssign(BaseModel):
    fiscal_id: int


def _to_dict(f: Fiscalizacao):
    return {
        'id': f.id,
        'uuid': str(f.uuid),
        'denuncia_id': f.denuncia_id,
        'fiscal_id': f.fiscal_id,
        'codigo': f.codigo,
        'status': f.status,
        'data_inicializacao': f.data_inicializacao.isoformat() if f.data_inicializacao is not None else None,
        'data_conclusao': f.data_conclusao.isoformat() if f.data_conclusao is not None else None,
        'observacoes': f.observacoes,
        'created_at': f.created_at.isoformat() if f.created_at is not None else None,
        'updated_at': f.updated_at.isoformat() if f.updated_at is not None else None,
    }


@router.post('/', status_code=201)
def create_fiscalizacao(payload: FiscalizacaoCreate, current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')

    db = SessionLocal()
    try:
        denuncia = db.query(Denuncia).filter(Denuncia.id == payload.complaint_id).first()
        if not denuncia:
            raise HTTPException(status_code=404, detail='Denúncia não encontrada')

        # Gerar código único simples
        codigo = f"FISC-{uuid.uuid4().hex[:8]}"

        fiscalizacao = Fiscalizacao(
            denuncia_id=denuncia.id,
            fiscal_id=current_user.id,
            codigo=codigo,
            observacoes=payload.observacoes,
            status=StatusFiscalizacao.AGUARDANDO
        )
        db.add(fiscalizacao)
        db.commit()
        db.refresh(fiscalizacao)
        return JSONResponse(_to_dict(fiscalizacao), status_code=201)
    finally:
        db.close()


@router.get('/')
def list_fiscalizacoes(status_filter: Optional[str] = None, fiscal_id: Optional[int] = None, limit: int = 50, offset: int = 0):
    db = SessionLocal()
    try:
        query = db.query(Fiscalizacao)
        if status_filter:
            query = query.filter(Fiscalizacao.status == status_filter)
        if fiscal_id:
            query = query.filter(Fiscalizacao.fiscal_id == fiscal_id)
        results = query.limit(limit).offset(offset).all()
        return [_to_dict(r) for r in results]
    finally:
        db.close()


@router.get('/minhas')
def list_my_fiscalizacoes(current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')
    db = SessionLocal()
    try:
        results = db.query(Fiscalizacao).filter(Fiscalizacao.fiscal_id == current_user.id).all()
        return [_to_dict(r) for r in results]
    finally:
        db.close()


@router.get('/{id}')
def get_fiscalizacao(id: int):
    db = SessionLocal()
    try:
        f = db.query(Fiscalizacao).filter(Fiscalizacao.id == id).first()
        if not f:
            raise HTTPException(status_code=404, detail='Fiscalização não encontrada')
        return _to_dict(f)
    finally:
        db.close()


@router.patch('/{id}/atribuir')
def assign_fiscalizacao(id: int, payload: FiscalizacaoAssign, current_user=Depends(get_current_user)):
    # Para simplicidade permitimos que qualquer usuário autenticado atribua — ajuste a autorização conforme regras de negócio
    db = SessionLocal()
    try:
        f = db.query(Fiscalizacao).filter(Fiscalizacao.id == id).first()
        if not f:
            raise HTTPException(status_code=404, detail='Fiscalização não encontrada')
        setattr(f, 'fiscal_id', payload.fiscal_id)
        db.add(f)
        db.commit()
        db.refresh(f)
        return _to_dict(f)
    finally:
        db.close()


@router.get('/{id}/historico')
def get_history(id: int):
    # Histórico de status/ações não implementado; retornar placeholder
    raise HTTPException(status_code=501, detail='Histórico não implementado')
