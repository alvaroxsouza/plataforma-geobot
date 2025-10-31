"""
Serviço para hash e verificação de senhas
"""
import bcrypt


class PasswordService:
    """Serviço para gerenciamento seguro de senhas"""

    @staticmethod
    def hash_senha(senha: str) -> str:
        """
        Gera um hash bcrypt da senha
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            Hash da senha em formato string
        """
        # Gera um salt e hash da senha
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds é um bom equilíbrio entre segurança e performance
        senha_bytes = senha.encode('utf-8')
        hash_bytes = bcrypt.hashpw(senha_bytes, salt)
        return hash_bytes.decode('utf-8')

    @staticmethod
    def verificar_senha(senha: str, hash_armazenado: str) -> bool:
        """
        Verifica se a senha corresponde ao hash armazenado
        
        Args:
            senha: Senha em texto plano a ser verificada
            hash_armazenado: Hash armazenado no banco de dados
            
        Returns:
            True se a senha corresponde, False caso contrário
        """
        try:
            senha_bytes = senha.encode('utf-8')
            hash_bytes = hash_armazenado.encode('utf-8')
            return bcrypt.checkpw(senha_bytes, hash_bytes)
        except Exception:
            # Em caso de erro (hash malformado, etc), retorna False
            return False

    @staticmethod
    def validar_forca_senha(senha: str) -> tuple[bool, list[str]]:
        """
        Valida a força de uma senha
        
        Args:
            senha: Senha a ser validada
            
        Returns:
            Tupla (é_válida, lista_de_problemas)
        """
        problemas = []
        
        if len(senha) < 8:
            problemas.append("Senha deve ter pelo menos 8 caracteres")
        
        if not any(c.isupper() for c in senha):
            problemas.append("Senha deve conter pelo menos uma letra maiúscula")
        
        if not any(c.islower() for c in senha):
            problemas.append("Senha deve conter pelo menos uma letra minúscula")
        
        if not any(c.isdigit() for c in senha):
            problemas.append("Senha deve conter pelo menos um número")
        
        # Caracteres especiais comuns
        caracteres_especiais = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in caracteres_especiais for c in senha):
            problemas.append("Senha deve conter pelo menos um caractere especial")
        
        return len(problemas) == 0, problemas

