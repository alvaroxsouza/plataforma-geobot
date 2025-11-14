"""Router (FastAPI) para rotas de etapas de fiscalização"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.core.database import get_db
from src.geobot_plataforma_backend.domain.entity.etapa_fiscalizacao_enum import EtapaFiscalizacaoEnum
from src.geobot_plataforma_backend.domain.service.etapa_fiscalizacao_service import EtapaFiscalizacaoService
from src.geobot_plataforma_backend.security.dependencies import get_current_user

router = APIRouter(prefix='/etapas-fiscalizacao', tags=['etapas-fiscalizacao'])


class IniciarFiscalizacaoPayload(BaseModel):
    """Payload para iniciar uma fiscalização"""
    fiscalizacao_id: int
    dados_iniciais: Optional[Dict[str, Any]] = None


class TransicionarEtapaPayload(BaseModel):
    """Payload para transicionar entre etapas"""
    etapa_nova: EtapaFiscalizacaoEnum
    dados: Optional[Dict[str, Any]] = None


class AtualizarProgressoPayload(BaseModel):
    """Payload para atualizar progresso"""
    progresso_percentual: float
    resultado: Optional[Dict[str, Any]] = None


class IniciarAnaliseIAPayload(BaseModel):
    """Payload para iniciar análise de IA"""
    etapa_id: int


class GerarRelatorioPayload(BaseModel):
    """Payload para gerar relatório"""
    titulo: str
    resumo_executivo: Optional[str] = None
    conclusoes: Optional[str] = None
    recomendacoes: Optional[str] = None


def _value_error_to_status(err: ValueError) -> int:
    mensagem = str(err).lower()
    if "não encontrada" in mensagem or "nao encontrada" in mensagem:
        return status.HTTP_404_NOT_FOUND
    return status.HTTP_400_BAD_REQUEST


@router.post('/{fiscalizacao_id}/iniciar', status_code=status.HTTP_201_CREATED)
def iniciar_fiscalizacao(
    fiscalizacao_id: int,
    payload: Optional[IniciarFiscalizacaoPayload] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Inicia uma fiscalização criando a etapa SOBREVOO"""
    service = EtapaFiscalizacaoService(db)
    try:
        dados_iniciais = payload.dados_iniciais if payload else None
        etapa = service.iniciar_fiscalizacao(fiscalizacao_id, dados_iniciais)
        return {
            'id': etapa.id,
            'fiscalizacao_id': etapa.fiscalizacao_id,
            'etapa': etapa.etapa.value,
            'progresso_percentual': etapa.progresso_percentual,
            'dados': etapa.dados,
            'created_at': etapa.created_at.isoformat() if etapa.created_at else None
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao iniciar fiscalização") from err


@router.post('/{fiscalizacao_id}/transicionar')
def transicionar_etapa(
    fiscalizacao_id: int,
    payload: TransicionarEtapaPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transiciona uma fiscalização para a próxima etapa"""
    service = EtapaFiscalizacaoService(db)
    try:
        etapa = service.transicionar_etapa(fiscalizacao_id, payload.etapa_nova, payload.dados)
        return {
            'id': etapa.id,
            'fiscalizacao_id': etapa.fiscalizacao_id,
            'etapa': etapa.etapa.value,
            'progresso_percentual': etapa.progresso_percentual,
            'dados': etapa.dados,
            'created_at': etapa.created_at.isoformat() if etapa.created_at else None
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao transicionar etapa") from err


@router.get('/{fiscalizacao_id}/progresso')
def obter_progresso(
    fiscalizacao_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém o progresso completo de uma fiscalização"""
    service = EtapaFiscalizacaoService(db)
    try:
        progresso = service.obter_progresso_completo(fiscalizacao_id)
        return progresso
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao obter progresso") from err


@router.patch('/etapa/{etapa_id}/progresso')
def atualizar_progresso(
    etapa_id: int,
    payload: AtualizarProgressoPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza o progresso de uma etapa"""
    service = EtapaFiscalizacaoService(db)
    try:
        etapa = service.atualizar_progresso(etapa_id, payload.progresso_percentual, payload.resultado)
        return {
            'id': etapa.id,
            'progresso_percentual': etapa.progresso_percentual,
            'resultado': etapa.resultado
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar progresso") from err


@router.post('/{fiscalizacao_id}/upload', status_code=status.HTTP_201_CREATED)
async def upload_arquivo(
    fiscalizacao_id: int,
    etapa_id: int = Form(...),
    tipo: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload de arquivo para a fiscalização (etapa ABASTECIMENTO)"""
    service = EtapaFiscalizacaoService(db)
    try:
        # TODO: Implementar upload real para blob storage
        # Por enquanto, retornar mock
        arquivo = service.registrar_arquivo(
            fiscalizacao_id=fiscalizacao_id,
            etapa_id=etapa_id,
            tipo=tipo,
            nome_original=file.filename or "arquivo",
            url_blob=f"/uploads/{fiscalizacao_id}/{file.filename}",
            tamanho_bytes=0,  # TODO: Calcular tamanho real
            mime_type=file.content_type or "application/octet-stream"
        )
        
        return {
            'id': arquivo.id,
            'fiscalizacao_id': arquivo.fiscalizacao_id,
            'tipo': arquivo.tipo,
            'nome_original': arquivo.nome_original,
            'url_blob': arquivo.url_blob,
            'created_at': arquivo.created_at.isoformat() if arquivo.created_at else None
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao fazer upload") from err


@router.get('/{fiscalizacao_id}/arquivos')
def listar_arquivos(
    fiscalizacao_id: int,
    tipo: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista arquivos de uma fiscalização"""
    service = EtapaFiscalizacaoService(db)
    try:
        arquivos = service.obter_arquivos(fiscalizacao_id, tipo)
        return [{
            'id': arquivo.id,
            'tipo': arquivo.tipo,
            'nome_original': arquivo.nome_original,
            'url_blob': arquivo.url_blob,
            'tamanho_bytes': arquivo.tamanho_bytes,
            'mime_type': arquivo.mime_type,
            'created_at': arquivo.created_at.isoformat() if arquivo.created_at else None
        } for arquivo in arquivos]
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar arquivos") from err


@router.post('/{fiscalizacao_id}/iniciar-analise')
def iniciar_analise_ia(
    fiscalizacao_id: int,
    payload: IniciarAnaliseIAPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Inicia análise de IA nas imagens (etapa ANALISE_IA)"""
    service = EtapaFiscalizacaoService(db)
    try:
        # TODO: Integrar com skypilot_service.py
        # Por enquanto, registrar resultado mock
        resultado = service.registrar_resultado_ia(
            etapa_id=payload.etapa_id,
            deteccoes=[
                {"tipo": "buraco", "confianca": 0.85, "localizacao": {"x": 100, "y": 200}}
            ],
            confianca_media=0.85,
            job_id=f"job_{fiscalizacao_id}",
            modelo_utilizado="yolov8",
            tempo_processamento=45.5
        )
        
        return {
            'id': resultado.id,
            'etapa_id': resultado.etapa_id,
            'job_id': resultado.job_id,
            'classificacao_geral': resultado.classificacao_geral,
            'confianca_media': resultado.confianca_media,
            'deteccoes': resultado.deteccoes,
            'status_processamento': resultado.status_processamento
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao iniciar análise") from err


@router.get('/etapa/{etapa_id}/resultado-ia')
def obter_resultado_ia(
    etapa_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém resultado da análise de IA de uma etapa"""
    service = EtapaFiscalizacaoService(db)
    try:
        resultado = service.obter_resultado_ia(etapa_id)
        if not resultado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado não encontrado")
        
        return {
            'id': resultado.id,
            'job_id': resultado.job_id,
            'classificacao_geral': resultado.classificacao_geral,
            'confianca_media': resultado.confianca_media,
            'deteccoes': resultado.deteccoes,
            'modelo_utilizado': resultado.modelo_utilizado,
            'status_processamento': resultado.status_processamento,
            'tempo_processamento_segundos': resultado.tempo_processamento_segundos
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao obter resultado") from err


@router.post('/{fiscalizacao_id}/gerar-relatorio', status_code=status.HTTP_201_CREATED)
def gerar_relatorio(
    fiscalizacao_id: int,
    etapa_id: int,
    payload: GerarRelatorioPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gera relatório da fiscalização (etapa RELATORIO)"""
    service = EtapaFiscalizacaoService(db)
    try:
        relatorio = service.criar_relatorio(
            fiscalizacao_id=fiscalizacao_id,
            etapa_id=etapa_id,
            titulo=payload.titulo,
            dados_relatorio={},  # TODO: Compilar dados das etapas anteriores
            resumo_executivo=payload.resumo_executivo,
            conclusoes=payload.conclusoes,
            recomendacoes=payload.recomendacoes
        )
        
        return {
            'id': relatorio.id,
            'fiscalizacao_id': relatorio.fiscalizacao_id,
            'titulo': relatorio.titulo,
            'status': relatorio.status,
            'created_at': relatorio.created_at.isoformat() if relatorio.created_at else None
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao gerar relatório") from err


@router.get('/{fiscalizacao_id}/relatorio')
def obter_relatorio(
    fiscalizacao_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém relatório de uma fiscalização"""
    service = EtapaFiscalizacaoService(db)
    try:
        relatorio = service.obter_relatorio(fiscalizacao_id)
        if not relatorio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatório não encontrado")
        
        return {
            'id': relatorio.id,
            'titulo': relatorio.titulo,
            'resumo_executivo': relatorio.resumo_executivo,
            'conclusoes': relatorio.conclusoes,
            'recomendacoes': relatorio.recomendacoes,
            'dados_relatorio': relatorio.dados_relatorio,
            'url_documento': relatorio.url_documento,
            'status': relatorio.status,
            'created_at': relatorio.created_at.isoformat() if relatorio.created_at else None
        }
    except ValueError as err:
        raise HTTPException(status_code=_value_error_to_status(err), detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao obter relatório") from err
