"""
Repository para operações de banco de dados relacionadas a usuários
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.geobot_plataforma_backend.domain.entity.usuario import Usuario


class UsuarioRepository:
    """Repository para gerenciar operações de banco de dados de usuários"""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, usuario: Usuario) -> Usuario:
        """
        Cria um novo usuário no banco de dados
        
        Args:
            usuario: Instância do modelo Usuario
            
        Returns:
            Usuario criado com ID gerado
        """
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """
        Busca um usuário por ID
        
        Args:
            usuario_id: ID do usuário
            
        Returns:
            Usuario ou None se não encontrado
        """
        return self.db.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.deleted_at.is_(None)
        ).first()

    def buscar_por_uuid(self, uuid: str) -> Optional[Usuario]:
        """
        Busca um usuário por UUID
        
        Args:
            uuid: UUID do usuário
            
        Returns:
            Usuario ou None se não encontrado
        """
        return self.db.query(Usuario).filter(
            Usuario.uuid == uuid,
            Usuario.deleted_at.is_(None)
        ).first()

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """
        Busca um usuário por email
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuario ou None se não encontrado
        """
        return self.db.query(Usuario).filter(
            func.lower(Usuario.email) == func.lower(email),
            Usuario.deleted_at.is_(None)
        ).first()

    def buscar_por_cpf(self, cpf: str) -> Optional[Usuario]:
        """
        Busca um usuário por CPF
        
        Args:
            cpf: CPF do usuário
            
        Returns:
            Usuario ou None se não encontrado
        """
        return self.db.query(Usuario).filter(
            Usuario.cpf == cpf,
            Usuario.deleted_at.is_(None)
        ).first()

    def atualizar(self, usuario: Usuario) -> Usuario:
        """
        Atualiza um usuário no banco de dados
        
        Args:
            usuario: Instância do modelo Usuario com dados atualizados
            
        Returns:
            Usuario atualizado
        """
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def email_existe(self, email: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se um email já está cadastrado
        
        Args:
            email: Email a ser verificado
            excluir_id: ID do usuário a ser excluído da verificação
            
        Returns:
            True se o email existe, False caso contrário
        """
        query = self.db.query(Usuario).filter(
            func.lower(Usuario.email) == func.lower(email),
            Usuario.deleted_at.is_(None)
        )
        
        if excluir_id:
            query = query.filter(Usuario.id != excluir_id)
        
        return query.first() is not None

    def cpf_existe(self, cpf: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se um CPF já está cadastrado
        
        Args:
            cpf: CPF a ser verificado
            excluir_id: ID do usuário a ser excluído da verificação
            
        Returns:
            True se o CPF existe, False caso contrário
        """
        query = self.db.query(Usuario).filter(
            Usuario.cpf == cpf,
            Usuario.deleted_at.is_(None)
        )
        
        if excluir_id:
            query = query.filter(Usuario.id != excluir_id)
        
        return query.first() is not None

    def incrementar_tentativas_login(self, usuario: Usuario) -> Usuario:
        """
        Incrementa o contador de tentativas de login do usuário
        
        Args:
            usuario: Instância do modelo Usuario
            
        Returns:
            Usuario atualizado
        """
        usuario.tentativas_login += 1
        return self.atualizar(usuario)

    def resetar_tentativas_login(self, usuario: Usuario) -> Usuario:
        """
        Reseta o contador de tentativas de login do usuário
        
        Args:
            usuario: Instância do modelo Usuario
            
        Returns:
            Usuario atualizado
        """
        usuario.tentativas_login = 0
        usuario.bloqueado_ate = None
        return self.atualizar(usuario)

