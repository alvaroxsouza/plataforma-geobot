"""Router FastAPI para endpoints de autenticação"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.core.database import get_db
from src.geobot_plataforma_backend.domain.service.auth_service import AuthService
from src.geobot_plataforma_backend.security.dependencies import get_current_user
from src.geobot_plataforma_backend.api.dtos.usuario_dto import UsuarioCadastroDTO, UsuarioLoginDTO
from src.geobot_plataforma_backend.domain.service.sessao_service import SessaoService
from src.geobot_plataforma_backend.security.service.jwt_service import JWTService


router = APIRouter(tags=['auth'])


class UsuarioCadastroModel(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    senha: str


class UsuarioLoginModel(BaseModel):
    email: EmailStr
    senha: str


@router.post('/cadastro', status_code=201)
def cadastrar_usuario(body: UsuarioCadastroModel, db: Session = Depends(get_db)):
    try:
        dados_dto = UsuarioCadastroDTO(
            cpf=body.cpf,
            nome=body.nome,
            email=body.email,
            senha=body.senha
        )

        auth_service = AuthService(db)
        usuario_criado = auth_service.cadastrar_usuario(dados_dto)
        return JSONResponse({'mensagem': 'Usuário cadastrado com sucesso', 'usuario': usuario_criado.to_dict()}, status_code=201)

    except ValueError as e:
        raise HTTPException(status_code=400, detail={'erro': 'Erro de validação', 'mensagem': str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={'erro': 'Erro interno do servidor', 'mensagem': 'Ocorreu um erro ao processar sua solicitação'})


@router.post('/login')
def login(body: UsuarioLoginModel, db: Session = Depends(get_db), request: Request = None):
    try:
        dados_dto = UsuarioLoginDTO(email=body.email, senha=body.senha)

        auth_service = AuthService(db)
        resultado = auth_service.autenticar(dados_dto)
        
        # Gera tokens e cria sessão
        jwt_service = JWTService()
        token, exp_timestamp = jwt_service.gerar_token(
            usuario_id=resultado.usuario.id,
            usuario_uuid=resultado.usuario.uuid,
            email=resultado.usuario.email
        )
        refresh_token = jwt_service.gerar_refresh_token()
        
        # Extrai informações do request
        user_agent = request.headers.get('user-agent', 'Unknown') if request else 'Unknown'
        x_forwarded_for = request.headers.get('x-forwarded-for') if request else None
        ip_address = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else (request.client.host if request else None)
        device_name = request.headers.get('x-device-name') if request else None
        
        # Cria nova sessão
        sessao_service = SessaoService(db)
        sessao = sessao_service.criar_sessao(
            usuario_id=resultado.usuario.id,
            token=token,
            refresh_token=refresh_token,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        resp = {
            'mensagem': 'Login realizado com sucesso',
            'token': token,
            'refresh_token': refresh_token,
            'sessao_uuid': str(sessao.uuid),
            'expira_em': exp_timestamp,
            **resultado.to_dict()
        }
        return JSONResponse(resp, status_code=200)

    except ValueError as e:
        print(e)
        raise HTTPException(status_code=401, detail={'erro': 'Credenciais inválidas', 'mensagem': str(e)})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail={'erro': 'Erro interno do servidor', 'mensagem': 'Ocorreu um erro ao processar sua solicitação'})


@router.post('/logout')
def logout(current_user=Depends(get_current_user), db: Session = Depends(get_db), authorization: Optional[str] = None):
    try:
        usuario = current_user
        
        # Se houver token, revoga a sessão correspondente
        if authorization:
            jwt_service = JWTService()
            token = jwt_service.extrair_token_do_header(authorization)
            
            if token:
                token_hash = SessaoService._hash_token(token)
                sessao_service = SessaoService(db)
                sessao = sessao_service.repository.buscar_por_token_hash(token_hash)
                
                if sessao:
                    sessao_service.revogar_sessao(sessao.id, "Logout pelo usuário")
        
        return JSONResponse({'mensagem': 'Logout realizado com sucesso', 'usuario': usuario.nome}, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={'erro': 'Erro interno do servidor', 'mensagem': 'Ocorreu um erro ao processar sua solicitação'})


@router.post('/refresh-token')
def refresh_token(body: dict, db: Session = Depends(get_db)):
    """
    Renova o token JWT usando o refresh token
    
    Body (JSON):
        - refresh_token: O refresh token recebido no login
    """
    try:
        refresh_token_str = body.get('refresh_token')
        
        if not refresh_token_str:
            raise HTTPException(
                status_code=400,
                detail={'erro': 'Parâmetro obrigatório', 'mensagem': 'refresh_token é obrigatório'}
            )
        
        # Busca a sessão pelo refresh token
        refresh_token_hash = SessaoService._hash_token(refresh_token_str)
        sessao_service = SessaoService(db)
        sessao = sessao_service.repository.buscar_por_refresh_token_hash(refresh_token_hash)
        
        if not sessao:
            raise HTTPException(
                status_code=401,
                detail={'erro': 'Refresh token inválido', 'mensagem': 'Refresh token não encontrado'}
            )
        
        # Verifica se pode renovar
        pode_renovar, motivo = sessao_service.pode_renovar_token(sessao)
        if not pode_renovar:
            sessao_service.registrar_tentativa_renovacao(sessao)
            raise HTTPException(
                status_code=401,
                detail={'erro': 'Não é possível renovar o token', 'mensagem': motivo}
            )
        
        # Gera novo token
        jwt_service = JWTService()
        novo_token, novo_exp = jwt_service.gerar_token(
            usuario_id=sessao.usuario_id,
            usuario_uuid=str(sessao.usuario.uuid),
            email=sessao.usuario.email,
            sessao_uuid=str(sessao.uuid)
        )
        
        # Atualiza o hash do token na sessão
        sessao.token_hash = SessaoService._hash_token(novo_token)
        sessao.registrar_atividade()
        sessao_service.repository.atualizar(sessao)
        
        return JSONResponse({
            'mensagem': 'Token renovado com sucesso',
            'token': novo_token,
            'expira_em': novo_exp,
            'sessao_uuid': str(sessao.uuid)
        }, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'erro': 'Erro ao renovar token', 'mensagem': str(e)}
        )


@router.get('/me')
def obter_usuario_atual(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        usuario = current_user
        
        # Buscar grupos do usuário
        grupos_list = []
        if hasattr(usuario, 'grupos') and usuario.grupos:
            for usuario_grupo in usuario.grupos:
                if hasattr(usuario_grupo, 'grupo') and usuario_grupo.grupo:
                    grupos_list.append({
                        'id': usuario_grupo.grupo.id,
                        'nome': usuario_grupo.grupo.nome,
                        'descricao': usuario_grupo.grupo.descricao
                    })
        
        return JSONResponse({'usuario': {
            'id': usuario.id,
            'uuid': str(usuario.uuid),
            'cpf': usuario.cpf,
            'nome': usuario.nome,
            'email': usuario.email,
            'ativo': usuario.ativo,
            'grupos': grupos_list
        }}, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={'erro': 'Erro interno do servidor', 'mensagem': 'Ocorreu um erro ao processar sua solicitação'})


@router.get('/validar-token')
def validar_token(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        usuario = current_user
        
        # Buscar grupos do usuário
        grupos_list = []
        if hasattr(usuario, 'grupos') and usuario.grupos:
            for usuario_grupo in usuario.grupos:
                if hasattr(usuario_grupo, 'grupo') and usuario_grupo.grupo:
                    grupos_list.append({
                        'id': usuario_grupo.grupo.id,
                        'nome': usuario_grupo.grupo.nome,
                        'descricao': usuario_grupo.grupo.descricao
                    })
        
        return JSONResponse({'valido': True, 'mensagem': 'Token válido', 'usuario': {
            'id': usuario.id,
            'uuid': str(usuario.uuid),
            'cpf': usuario.cpf,
            'nome': usuario.nome,
            'email': usuario.email,
            'ativo': usuario.ativo,
            'grupos': grupos_list
        }}, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={'erro': 'Erro interno do servidor', 'mensagem': 'Ocorreu um erro ao processar sua solicitação'})
