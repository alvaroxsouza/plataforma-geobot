"""Router FastAPI para endpoints de autenticação"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.core.database import get_db
from src.geobot_plataforma_backend.domain.service.auth_service import AuthService
from src.geobot_plataforma_backend.security.dependencies import get_current_user
from src.geobot_plataforma_backend.api.dtos.usuario_dto import UsuarioCadastroDTO, UsuarioLoginDTO


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
def login(body: UsuarioLoginModel, db: Session = Depends(get_db)):
    try:
        dados_dto = UsuarioLoginDTO(email=body.email, senha=body.senha)

        auth_service = AuthService(db)
        resultado = auth_service.autenticar(dados_dto)
        resp = {'mensagem': 'Login realizado com sucesso', **resultado.to_dict()}
        return JSONResponse(resp, status_code=200)

    except ValueError as e:
        print(e)
        raise HTTPException(status_code=401, detail={'erro': 'Credenciais inválidas', 'mensagem': str(e)})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail={'erro': 'Erro interno do servidor', 'mensagem': 'Ocorreu um erro ao processar sua solicitação'})


@router.post('/logout')
def logout(current_user=Depends(get_current_user)):
    try:
        usuario = current_user
        return JSONResponse({'mensagem': 'Logout realizado com sucesso', 'usuario': usuario.nome}, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={'erro': 'Erro interno do servidor', 'mensagem': 'Ocorreu um erro ao processar sua solicitação'})


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
