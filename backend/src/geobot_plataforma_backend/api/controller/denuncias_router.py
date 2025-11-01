"""Router FastAPI para operações de denúncias."""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.geobot_plataforma_backend.core.database import SessionLocal
from src.geobot_plataforma_backend.domain.entity.denuncia import Denuncia
from src.geobot_plataforma_backend.domain.entity.endereco import Endereco
from src.geobot_plataforma_backend.security.dependencies import get_current_user
from src.geobot_plataforma_backend.domain.entity.enums import StatusDenuncia

router = APIRouter(prefix="/denuncias", tags=["denuncias"])


class DenunciaCreate(BaseModel):
    street_address: Optional[str]
    subject: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    observacoes: Optional[str]
    endereco_id: Optional[int]


class DenunciaUpdate(BaseModel):
    street_address: Optional[str]
    observacoes: Optional[str]


def _denuncia_to_dict(denuncia: Any) -> dict:
    created_at = getattr(denuncia, "created_at", None)
    updated_at = getattr(denuncia, "updated_at", None)
    return {
        "id": getattr(denuncia, "id", None),
        "uuid": str(getattr(denuncia, "uuid", "")),
        "usuario_id": getattr(denuncia, "usuario_id", None),
        "endereco_id": getattr(denuncia, "endereco_id", None),
        "status": getattr(denuncia, "status", None),
        "categoria": getattr(denuncia, "categoria", None),
        "prioridade": getattr(denuncia, "prioridade", None),
        "observacao": getattr(denuncia, "observacao", None),
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


@router.post("/", status_code=201)
def criar_denuncia(payload: DenunciaCreate, current_user=Depends(get_current_user)):
    """Cria nova denúncia. Requer `endereco_id` ou enviar um endereço com campos mínimos."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação requerida")

    if not payload.endereco_id and not payload.street_address:
        raise HTTPException(
            status_code=400,
            detail={
                "erro": "Endereço ausente",
                "mensagem": "Informe `endereco_id` existente ou envie endereço completo (logradouro, bairro, cidade, estado, cep)",
            },
        )

    db = SessionLocal()
    try:
        if payload.endereco_id:
            endereco = db.query(Endereco).filter(Endereco.id == payload.endereco_id).first()
            if not endereco:
                raise HTTPException(
                    status_code=400,
                    detail={"erro": "Endereço inválido", "mensagem": "endereco_id não encontrado"},
                )
            endereco_id = endereco.id
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "erro": "Criação de endereço não implementada",
                    "mensagem": "Por favor informe endereco_id até que criação completa de endereço seja implementada",
                },
            )

        denuncia = Denuncia(
            usuario_id=current_user.id,
            endereco_id=endereco_id,
            observacao=payload.observacoes or payload.subject or "",
            categoria="outros",
        )
        db.add(denuncia)
        db.commit()
        db.refresh(denuncia)

        return JSONResponse(_denuncia_to_dict(denuncia), status_code=201)
    finally:
        db.close()


@router.get("/", response_model=List[dict])
def listar_denuncias(status: Optional[str] = None, subject: Optional[str] = None, limit: int = 50, offset: int = 0):
    db = SessionLocal()
    try:
        query = db.query(Denuncia)
        if status:
            query = query.filter(Denuncia.status == status)
        if subject:
            query = query.filter(Denuncia.observacao.ilike(f"%{subject}%"))
        query = query.limit(limit).offset(offset)
        resultados = query.all()
        return [_denuncia_to_dict(d) for d in resultados]
    finally:
        db.close()


@router.get("/pending")
def listar_pendentes():
    db = SessionLocal()
    try:
        resultados = db.query(Denuncia).filter(Denuncia.status == StatusDenuncia.PENDENTE).all()
        return [_denuncia_to_dict(d) for d in resultados]
    finally:
        db.close()


@router.get("/minhas")
def listar_minhas_denuncias(current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação requerida")
    db = SessionLocal()
    try:
        resultados = db.query(Denuncia).filter(Denuncia.usuario_id == current_user.id).all()
        return [_denuncia_to_dict(d) for d in resultados]
    finally:
        db.close()


@router.get("/{id}")
def obter_denuncia(id: int):
    db = SessionLocal()
    try:
        denuncia = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not denuncia:
            raise HTTPException(status_code=404, detail="Denúncia não encontrada")
        return _denuncia_to_dict(denuncia)
    finally:
        db.close()


@router.patch("/{id}")
def atualizar_denuncia(id: int, payload: DenunciaUpdate, current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação requerida")
    db = SessionLocal()
    try:
        denuncia = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not denuncia:
            raise HTTPException(status_code=404, detail="Denúncia não encontrada")
        if getattr(denuncia, "usuario_id", None) != current_user.id:
            raise HTTPException(status_code=403, detail="Somente o autor pode atualizar a denúncia")
        if getattr(denuncia, "status", None) != StatusDenuncia.PENDENTE:
            raise HTTPException(status_code=400, detail="Apenas denúncias pendentes podem ser atualizadas")
        if payload.observacoes is not None:
            observacao_atual = getattr(denuncia, "observacao", "")
            setattr(denuncia, "observacao", payload.observacoes or observacao_atual)
        db.add(denuncia)
        db.commit()
        db.refresh(denuncia)
        return _denuncia_to_dict(denuncia)
    finally:
        db.close()


@router.post("/{id}/rejeitar")
def rejeitar_denuncia(
    id: int,
    motivo_rejeicao: Optional[str] = Form(None),
    denuncia_duplicada_id: Optional[int] = Form(None),
    current_user=Depends(get_current_user),
):
    """Marca denúncia como arquivada. Armazena a justificativa em `observacao` por enquanto."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação requerida")
    db = SessionLocal()
    try:
        denuncia = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not denuncia:
            raise HTTPException(status_code=404, detail="Denúncia não encontrada")
        setattr(denuncia, "status", StatusDenuncia.ARQUIVADA)
        observacao_atual = getattr(denuncia, "observacao", "") or ""
        if motivo_rejeicao:
            observacao_atual += f"\n[Rejeitada] {motivo_rejeicao}"
        if denuncia_duplicada_id:
            observacao_atual += f"\n[Duplicada de] {denuncia_duplicada_id}"
        setattr(denuncia, "observacao", observacao_atual)
        db.add(denuncia)
        db.commit()
        db.refresh(denuncia)
        return _denuncia_to_dict(denuncia)
    finally:
        db.close()


@router.post("/{id}/cancelar")
def cancelar_denuncia(id: int, dados: dict, current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação requerida")
    db = SessionLocal()
    try:
        denuncia = db.query(Denuncia).filter(Denuncia.id == id).first()
        if not denuncia:
            raise HTTPException(status_code=404, detail="Denúncia não encontrada")
        if getattr(denuncia, "usuario_id", None) != current_user.id:
            raise HTTPException(status_code=403, detail="Somente o autor pode cancelar a denúncia")
        setattr(denuncia, "status", StatusDenuncia.CANCELADA)
        observacao_atual = getattr(denuncia, "observacao", "") or ""
        motivo = dados.get("motivo") if isinstance(dados, dict) else None
        if motivo:
            observacao_atual += f"\n[Cancelada] {motivo}"
        setattr(denuncia, "observacao", observacao_atual)
        db.add(denuncia)
        db.commit()
        db.refresh(denuncia)
        return _denuncia_to_dict(denuncia)
    finally:
        db.close()


@router.post("/{id}/analyze")
def analisar_imagem(id: int, file: UploadFile = File(...), current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação requerida")

    if not file:
        raise HTTPException(status_code=400, detail="Arquivo não fornecido")

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": None,
        "message": "Upload recebido (processamento/armazenamento não implementado)",
    }


@router.get("/{id}/report/download")
def download_relatorio(id: int, current_user=Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Geração de relatório não implementada")
