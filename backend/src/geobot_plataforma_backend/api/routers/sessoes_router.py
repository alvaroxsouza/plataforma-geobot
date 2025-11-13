"""
Router FastAPI para endpoints de gerenciamento de sessões
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.core.database import get_db
from src.geobot_plataforma_backend.security.dependencies import get_current_user
from src.geobot_plataforma_backend.domain.service.sessao_service import SessaoService
from src.geobot_plataforma_backend.security.service.jwt_service import JWTService


router = APIRouter(tags=['sessoes'], prefix='/sessoes')


def obter_user_agent_e_ip(request: Request) -> tuple[str, str]:
    """Extrai User-Agent e IP do request"""
    user_agent = request.headers.get('user-agent', 'Unknown')
    
    # Tenta obter IP real (considerando proxies)
    x_forwarded_for = request.headers.get('x-forwarded-for')
    ip_address = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.client.host
    
    return user_agent, ip_address


@router.get('')
def listar_sessoes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Lista todas as sessões ativas do usuário autenticado
    """
    try:
        sessao_service = SessaoService(db)
        sessoes = sessao_service.obter_sessoes_ativas(current_user.id)
        
        return JSONResponse({
            'mensagem': 'Sessões recuperadas com sucesso',
            'total': len(sessoes),
            'sessoes': [s.to_dict() for s in sessoes]
        }, status_code=200)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao listar sessões', 'mensagem': str(e)}
        )


@router.get('/relatorio')
def gerar_relatorio_sessoes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera um relatório completo de sessões do usuário
    """
    try:
        sessao_service = SessaoService(db)
        relatorio = sessao_service.gerar_relatorio_sessoes(current_user.id)
        
        return JSONResponse({
            'mensagem': 'Relatório gerado com sucesso',
            **relatorio
        }, status_code=200)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao gerar relatório', 'mensagem': str(e)}
        )


@router.delete('/{sessao_uuid}')
def revogar_sessao(
    sessao_uuid: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoga uma sessão específica do usuário
    """
    try:
        sessao_service = SessaoService(db)
        
        # Verifica se a sessão pertence ao usuário
        sessao = sessao_service.repository.buscar_por_uuid(sessao_uuid)
        if not sessao or sessao.usuario_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail={'erro': 'Sessão não encontrada', 'mensagem': 'A sessão não pertence ao usuário'}
            )
        
        # Revoga a sessão
        sessao_service.revogar_sessao(sessao.id, "Revogada pelo usuário")
        
        return JSONResponse({
            'mensagem': 'Sessão revogada com sucesso',
            'sessao_uuid': sessao_uuid
        }, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao revogar sessão', 'mensagem': str(e)}
        )


@router.post('/revogar-todas')
def revogar_todas_sessoes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoga todas as sessões do usuário (logout em todos os dispositivos)
    """
    try:
        sessao_service = SessaoService(db)
        quantidade = sessao_service.revogar_todas_usuario(current_user.id)
        
        return JSONResponse({
            'mensagem': f'{quantidade} sessões revogadas com sucesso',
            'total_revogadas': quantidade
        }, status_code=200)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao revogar sessões', 'mensagem': str(e)}
        )


@router.post('/manter-ativa')
def manter_sessao_ativa(
    sessao_uuid: str = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza a atividade da sessão para evitar timeout
    
    Body (JSON):
        - sessao_uuid: UUID da sessão a manter ativa
    """
    try:
        if not sessao_uuid:
            raise HTTPException(
                status_code=400,
                detail={'erro': 'Parâmetro obrigatório', 'mensagem': 'sessao_uuid é obrigatório'}
            )
        
        sessao_service = SessaoService(db)
        atualizado = sessao_service.manter_sessao_ativa(current_user.id, sessao_uuid)
        
        if not atualizado:
            raise HTTPException(
                status_code=404,
                detail={'erro': 'Sessão não encontrada', 'mensagem': 'A sessão não está ativa'}
            )
        
        return JSONResponse({
            'mensagem': 'Atividade da sessão atualizada',
            'sessao_uuid': sessao_uuid
        }, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao atualizar atividade', 'mensagem': str(e)}
        )


@router.post('/revogar-outras')
def revogar_outras_sessoes(
    sessao_uuid_manter: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoga todas as sessões exceto uma (útil para logout de outros dispositivos)
    
    Body (JSON):
        - sessao_uuid_manter: UUID da sessão a manter ativa
    """
    try:
        sessao_service = SessaoService(db)
        
        # Busca a sessão para verificar ID
        sessao = sessao_service.repository.buscar_por_uuid(sessao_uuid_manter)
        if not sessao or sessao.usuario_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail={'erro': 'Sessão inválida', 'mensagem': 'A sessão a manter não foi encontrada'}
            )
        
        quantidade = sessao_service.revogar_outras_sessoes(current_user.id, sessao.id)
        
        return JSONResponse({
            'mensagem': f'{quantidade} sessões revogadas. Você permanece conectado apenas neste dispositivo',
            'total_revogadas': quantidade
        }, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao revogar sessões', 'mensagem': str(e)}
        )


@router.get('/tempo-restante')
def obter_tempo_restante(
    authorization: Optional[str] = Header(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém o tempo restante de um token JWT
    """
    try:
        jwt_service = JWTService()
        token = jwt_service.extrair_token_do_header(authorization)
        
        if not token:
            raise HTTPException(
                status_code=400,
                detail={'erro': 'Token não fornecido', 'mensagem': 'Authorization header é obrigatório'}
            )
        
        payload = jwt_service.validar_token(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail={'erro': 'Token inválido', 'mensagem': 'Token não pode ser validado'}
            )
        
        tempo_restante = jwt_service.obter_tempo_restante(payload.exp)
        
        return JSONResponse({
            'tempo_restante_segundos': tempo_restante,
            'tempo_restante_minutos': tempo_restante // 60,
            'expira_em': payload.exp,
            'proximo_refresh_em': payload.exp - (300)  # 5 minutos antes de expirar
        }, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao obter tempo restante', 'mensagem': str(e)}
        )
