"""
Serviço de autenticação e gerenciamento de usuários
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.geobot_plataforma_backend.domain.entity.usuario import Usuario
from src.geobot_plataforma_backend.domain.repository.usuario_repository import UsuarioRepository
from src.geobot_plataforma_backend.security.service.password_service import PasswordService
from src.geobot_plataforma_backend.security.service.jwt_service import JWTService
from src.geobot_plataforma_backend.api.dtos.usuario_dto import (
    UsuarioCadastroDTO,
    UsuarioLoginDTO,
    UsuarioResponseDTO,
    LoginResponseDTO
)


class AuthService:
    """Serviço para operações de autenticação e gerenciamento de usuários"""

    # Constantes para controle de tentativas de login
    MAX_TENTATIVAS_LOGIN = 5
    TEMPO_BLOQUEIO_MINUTOS = 30

    def __init__(self, db: Session):
        self.db = db
        self.repository = UsuarioRepository(db)
        self.password_service = PasswordService()
        self.jwt_service = JWTService()

    def cadastrar_usuario(self, dados: UsuarioCadastroDTO) -> UsuarioResponseDTO:
        """
        Cadastra um novo usuário no sistema
        
        Args:
            dados: DTO com os dados do usuário
            
        Returns:
            DTO com os dados do usuário criado
            
        Raises:
            ValueError: Se houver erro de validação
        """
        # Validar se email já existe
        if self.repository.email_existe(dados.email):
            raise ValueError("Email já cadastrado no sistema")

        # Validar se CPF já existe
        if self.repository.cpf_existe(dados.cpf):
            raise ValueError("CPF já cadastrado no sistema")

        # Validar força da senha
        senha_valida, problemas = self.password_service.validar_forca_senha(dados.senha)
        if not senha_valida:
            raise ValueError(f"Senha não atende aos requisitos: {'; '.join(problemas)}")

        # Criar hash da senha
        senha_hash = self.password_service.hash_senha(dados.senha)

        # Criar entidade Usuario
        novo_usuario = Usuario(
            cpf=dados.cpf,
            nome=dados.nome.strip(),
            email=dados.email.lower().strip(),
            senha_hash=senha_hash,
            ativo=True,
            tentativas_login=0
        )

        # Salvar no banco
        usuario_criado = self.repository.criar(novo_usuario)

        # Retornar DTO
        return UsuarioResponseDTO.from_entity(usuario_criado)

    def autenticar(self, dados: UsuarioLoginDTO) -> LoginResponseDTO:
        """
        Autentica um usuário e retorna um token JWT
        
        Args:
            dados: DTO com email e senha
            
        Returns:
            DTO com token e dados do usuário
            
        Raises:
            ValueError: Se as credenciais forem inválidas ou conta bloqueada
        """
        # Buscar usuário por email
        usuario = self.repository.buscar_por_email(dados.email)

        if not usuario:
            raise ValueError("Email ou senha inválidos")

        # Verificar se o usuário está ativo
        if not usuario.ativo:
            raise ValueError("Usuário inativo. Entre em contato com o administrador")

        # Verificar se está bloqueado por tentativas de login
        if usuario.bloqueado_ate:
            now = datetime.now(timezone.utc)
            bloqueado_ate = usuario.bloqueado_ate.replace(tzinfo=timezone.utc) if usuario.bloqueado_ate.tzinfo is None else usuario.bloqueado_ate
            if now < bloqueado_ate:
                tempo_restante = (bloqueado_ate - now).seconds // 60
                raise ValueError(
                    f"Conta temporariamente bloqueada devido a múltiplas tentativas de login. "
                    f"Tente novamente em {tempo_restante} minutos"
                )
            else:
                # Desbloqueio automático se o tempo passou
                usuario = self.repository.resetar_tentativas_login(usuario)

        # Verificar senha
        if not self.password_service.verificar_senha(dados.senha, usuario.senha_hash):
            # Incrementar tentativas de login
            usuario = self.repository.incrementar_tentativas_login(usuario)

            # Bloquear se atingiu o máximo de tentativas
            if usuario.tentativas_login >= self.MAX_TENTATIVAS_LOGIN:
                usuario.bloqueado_ate = datetime.now(timezone.utc) + timedelta(minutes=self.TEMPO_BLOQUEIO_MINUTOS)
                self.repository.atualizar(usuario)
                raise ValueError(
                    f"Conta bloqueada por {self.TEMPO_BLOQUEIO_MINUTOS} minutos devido a "
                    f"múltiplas tentativas de login com falha"
                )

            tentativas_restantes = self.MAX_TENTATIVAS_LOGIN - usuario.tentativas_login
            raise ValueError(
                f"Email ou senha inválidos. {tentativas_restantes} tentativa(s) restante(s) "
                f"antes do bloqueio temporário"
            )

        # Login bem-sucedido - resetar tentativas
        usuario.tentativas_login = 0
        usuario.bloqueado_ate = None
        usuario.data_ultimo_login = datetime.now(timezone.utc)
        usuario = self.repository.atualizar(usuario)

        # Gerar token JWT
        token, exp_timestamp = self.jwt_service.gerar_token(
            usuario.id,
            str(usuario.uuid),
            usuario.email
        )

        # Calcular tempo de expiração em segundos
        expires_in = self.jwt_service.obter_tempo_restante(exp_timestamp)

        # Retornar resposta
        return LoginResponseDTO(
            access_token=token,
            token_type="Bearer",
            expires_in=expires_in,
            usuario=UsuarioResponseDTO.from_entity(usuario)
        )

    def validar_token(self, token: str) -> Optional[UsuarioResponseDTO]:
        """
        Valida um token JWT e retorna os dados do usuário
        
        Args:
            token: Token JWT
            
        Returns:
            DTO com dados do usuário ou None se token inválido
        """
        # Validar token
        payload = self.jwt_service.validar_token(token)
        
        if not payload:
            return None

        # Buscar usuário
        usuario = self.repository.buscar_por_id(payload.usuario_id)

        if not usuario or not usuario.ativo:
            return None

        return UsuarioResponseDTO.from_entity(usuario)

    def obter_usuario_por_uuid(self, uuid: str) -> Optional[UsuarioResponseDTO]:
        """
        Busca um usuário por UUID
        
        Args:
            uuid: UUID do usuário
            
        Returns:
            DTO com dados do usuário ou None se não encontrado
        """
        usuario = self.repository.buscar_por_uuid(uuid)
        
        if not usuario:
            return None
        
        return UsuarioResponseDTO.from_entity(usuario)

