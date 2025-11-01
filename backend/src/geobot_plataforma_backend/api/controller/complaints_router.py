"""Router FastAPI para operações de denúncias (complaints)

Endpoints implementados (compatíveis com frontend `services/complaints.ts`):
- POST /complaints/           -> criar denúncia (requer `endereco_id` ou objeto `endereco` com campos mínimos)
- GET  /complaints/           -> listar denúncias (filtros básicos: status, subject, limit, offset)
- GET  /complaints/pending    -> listar pendentes
- GET  /complaints/minhas     -> listar denúncias do usuário autenticado
- GET  /complaints/{id}       -> obter denúncia por id
- PATCH /complaints/{id}      -> atualizar observação (apenas proprietário e status PENDENTE)
- POST /complaints/{id}/rejeitar  -> marcar como arquivada (usa justificativa)
- POST /complaints/{id}/cancelar  -> marcar como cancelada (apenas proprietário)
- POST /complaints/{id}/analyze   -> endpoint placeholder para upload de imagem (não implementado de storage)
- GET  /complaints/{id}/report/download -> placeholder (501 Not Implemented)

Nota: esta implementação é intencionalmente mínima. Há validações/recursos (storage de arquivos, geração de PDF, campos de endereço completos)
que devem ser completados conforme regras de negócio.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.geobot_plataforma_backend.core.database import SessionLocal
from src.geobot_plataforma_backend.domain.entity.denuncia import Denuncia
from src.geobot_plataforma_backend.domain.entity.endereco import Endereco
from src.geobot_plataforma_backend.domain.entity.arquivo import Arquivo
from src.geobot_plataforma_backend.security.dependencies import get_current_user
from src.geobot_plataforma_backend.domain.entity.enums import StatusDenuncia

router = APIRouter()


class ComplaintCreate(BaseModel):
    street_address: Optional[str]
    subject: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    observacoes: Optional[str]
    endereco_id: Optional[int]


class ComplaintUpdate(BaseModel):
    street_address: Optional[str]
    observacoes: Optional[str]


def _denuncia_to_dict(denuncia: Denuncia):
    return {
        'id': denuncia.id,
        'uuid': str(denuncia.uuid),
        'usuario_id': denuncia.usuario_id,
        'endereco_id': denuncia.endereco_id,
        'status': denuncia.status,
        'categoria': denuncia.categoria,
        'prioridade': denuncia.prioridade,
        'observacao': denuncia.observacao,
        'created_at': denuncia.created_at.isoformat() if denuncia.created_at else None,
        'updated_at': denuncia.updated_at.isoformat() if denuncia.updated_at else None,
    }


@router.post('/', status_code=201)
def create_complaint(payload: ComplaintCreate, current_user=Depends(get_current_user)):
    """Cria nova denúncia. Requer `endereco_id` ou enviar um objeto `endereco` com campos mínimos.
    Para simplicidade, aqui aceitamos `endereco_id` ou retornamos 400 instruindo os campos necessários.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')

    if not payload.endereco_id and not payload.street_address:
        raise HTTPException(status_code=400, detail={'erro': 'Endereço ausente', 'mensagem': 'Informe `endereco_id` existente ou envie endereço completo (logradouro, bairro, cidade, estado, cep)'})

    db = SessionLocal()
    try:
        if payload.endereco_id:
            endereco = db.query(Endereco).filter(Endereco.id == payload.endereco_id).first()
            if not endereco:
                raise HTTPException(status_code=400, detail={'erro': 'Endereço inválido', 'mensagem': 'endereco_id não encontrado'})
            endereco_id = endereco.id
        else:
            # Não criamos o endereço automaticamente aqui — exigir campos completos seria ideal.
            raise HTTPException(status_code=400, detail={'erro': 'Criação de endereço não implementada', 'mensagem': 'Por favor informe endereco_id até que criação completa de endereço seja implementada'})

        denuncia = Denuncia(
            usuario_id=current_user.id,
            endereco_id=endereco_id,
            observacao=payload.observacoes or payload.subject or '',
            categoria='outros'
        )
        db.add(denuncia)
        db.commit()
        db.refresh(denuncia)

        return JSONResponse(_denuncia_to_dict(denuncia), status_code=201)
    finally:
        db.close()


@router.get('/', response_model=List[dict])
def list_complaints(status: Optional[str] = None, subject: Optional[str] = None, limit: int = 50, offset: int = 0):
    db = SessionLocal()
    try:
        query = db.query(Denuncia)
        if status:
            query = query.filter(Denuncia.status == status)
        if subject:
            query = query.filter(Denuncia.observacao.ilike(f"%{subject}%"))
        query = query.limit(limit).offset(offset)
        results = query.all()
        return [_denuncia_to_dict(d) for d in results]
    finally:
        db.close()


@router.get('/pending')
def list_pending():
    db = SessionLocal()
    try:
        results = db.query(Denuncia).filter(Denuncia.status == StatusDenuncia.PENDENTE).all()
        return [_denuncia_to_dict(d) for d in results]
    finally:
        db.close()


@router.get('/minhas')
def list_my_complaints(current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')
    db = SessionLocal()
    try:
        results = db.query(Denuncia).filter(Denuncia.usuario_id == current_user.id).all()
        return [_denuncia_to_dict(d) for d in results]
    finally:
        db.close()


@router.get('/{id}')
def get_complaint(id: int):
    db = SessionLocal()
    try:
        d = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not d:
            raise HTTPException(status_code=404, detail='Denúncia não encontrada')
        return _denuncia_to_dict(d)
    finally:
        db.close()


@router.patch('/{id}')
def update_complaint(id: int, payload: ComplaintUpdate, current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')
    db = SessionLocal()
    try:
        d = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not d:
            raise HTTPException(status_code=404, detail='Denúncia não encontrada')
        if d.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail='Somente o autor pode atualizar a denúncia')
        if d.status != StatusDenuncia.PENDENTE:
            raise HTTPException(status_code=400, detail='Apenas denúncias pendentes podem ser atualizadas')
        if payload.observacoes is not None:
            d.observacao = payload.observacoes
        db.add(d)
        db.commit()
        db.refresh(d)
        return _denuncia_to_dict(d)
    finally:
        db.close()


@router.post('/{id}/rejeitar')
def reject_complaint(id: int, motivo_rejeicao: Optional[str] = Form(None), denuncia_duplicada_id: Optional[int] = Form(None), current_user=Depends(get_current_user)):
    """Marca denúncia como arquivada. Armazenamos a justificativa em `observacao` por enquanto."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')
    db = SessionLocal()
    try:
        d = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not d:
            raise HTTPException(status_code=404, detail='Denúncia não encontrada')
        d.status = StatusDenuncia.ARQUIVADA
        if motivo_rejeicao:
            d.observacao = (d.observacao or '') + f"\n[Rejeitada] {motivo_rejeicao}"
        if denuncia_duplicada_id:
            d.observacao = (d.observacao or '') + f"\n[Duplicada de] {denuncia_duplicada_id}"
        db.add(d)
        db.commit()
        db.refresh(d)
        return _denuncia_to_dict(d)
    finally:
        db.close()


@router.post('/{id}/cancelar')
def cancel_complaint(id: int, data: dict, current_user=Depends(get_current_user)):
    # data: { motivo: string }
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')
    db = SessionLocal()
    try:
        d = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not d:
            raise HTTPException(status_code=404, detail='Denúncia não encontrada')
        if d.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail='Somente o autor pode cancelar a denúncia')
        d.status = StatusDenuncia.CANCELADA
        motivo = data.get('motivo') if isinstance(data, dict) else None
        if motivo:
            d.observacao = (d.observacao or '') + f"\n[Cancelada] {motivo}"
        db.add(d)
        db.commit()
        db.refresh(d)
        return _denuncia_to_dict(d)
    finally:
        db.close()


@router.post('/{id}/analyze')
def analyze_image(id: int, file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """Endpoint placeholder para upload de imagem. Não realiza armazenamento.
    Retorna informações básicas do arquivo recebido.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação requerida')

    # Rejeitamos por enquanto se não houver arquivo
    if not file:
        raise HTTPException(status_code=400, detail='Arquivo não fornecido')

    # Não salvamos o arquivo em storage nesta etapa — retornar metadados mínimos
    return {
        'filename': file.filename,
        'content_type': file.content_type,
        'size': None,
        'message': 'Upload recebido (processamento/armazenamento não implementado)'
    }


@router.get('/{id}/report/download')
def download_report(id: int, current_user=Depends(get_current_user)):
    # Placeholder: geração/retorno de PDF não implementado
    raise HTTPException(status_code=501, detail='Geração de relatório não implementada')
