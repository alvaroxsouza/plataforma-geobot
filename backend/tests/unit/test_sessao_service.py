"""
Testes básicos para o sistema de controle de sessão
"""
from datetime import datetime, timedelta, timezone
from src.geobot_plataforma_backend.domain.entity.sessao import Sessao
from src.geobot_plataforma_backend.domain.service.sessao_service import SessaoService
from src.geobot_plataforma_backend.security.service.jwt_service import JWTService


def test_sessao_esta_ativa():
    """Testa se uma sessão está ativa"""
    now = datetime.now(timezone.utc)
    
    # Sessão ativa
    sessao = Sessao(
        usuario_id=1,
        token_hash="hash_token",
        expira_em=now + timedelta(hours=1),
        ativa=True
    )
    assert sessao.esta_ativa() is True

    # Sessão inativa
    sessao.ativa = False
    assert sessao.esta_ativa() is False

    # Sessão expirada
    sessao.ativa = True
    sessao.expira_em = now - timedelta(hours=1)
    assert sessao.esta_ativa() is False

    print("✓ test_sessao_esta_ativa passou")


def test_revogar_sessao():
    """Testa revogação de sessão"""
    sessao = Sessao(
        usuario_id=1,
        token_hash="hash_token",
        expira_em=datetime.now(timezone.utc) + timedelta(hours=1),
        ativa=True
    )
    
    assert sessao.revogada_em is None
    sessao.revogar("Teste")
    assert sessao.revogada_em is not None
    assert sessao.ativa is False
    assert sessao.motivo_revogacao == "Teste"
    
    print("✓ test_revogar_sessao passou")


def test_hash_token():
    """Testa hash de token"""
    token = "meu_token_super_secreto"
    hash1 = SessaoService._hash_token(token)
    hash2 = SessaoService._hash_token(token)
    
    assert hash1 == hash2
    assert len(hash1) == 64
    assert hash1 != token
    
    print("✓ test_hash_token passou")


def test_gerar_refresh_token():
    """Testa geração de refresh token"""
    jwt_service = JWTService()
    token1 = jwt_service.gerar_refresh_token()
    token2 = jwt_service.gerar_refresh_token()
    
    assert token1 is not None
    assert token2 is not None
    assert token1 != token2
    assert len(token1) > 20
    
    print("✓ test_gerar_refresh_token passou")


if __name__ == "__main__":
    test_sessao_esta_ativa()
    test_revogar_sessao()
    test_hash_token()
    test_gerar_refresh_token()
    
    print("\n✅ Testes unitários do sistema de sessão executados!")
