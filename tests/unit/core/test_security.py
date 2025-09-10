from jose import jwt

from app.core import security

def test_gerar_e_verificar_senha():
    """
    Testa se a geração de hash e a verificação de senha funcionam em conjunto.
    """
    senha_plana = "minhaSenha123"
    hash_senha = security.gerar_hash_senha(senha_plana)

    assert security.verificar_senha(senha_plana, hash_senha) is True
    assert security.verificar_senha("senha_errada", hash_senha) is False

def test_gerar_token_jwt(mocker):
    """
    Testa a geração de um token JWT, mocando as settings.
    """
    mocker.patch("app.core.security.settings.CHAVE_SEGURANCA_JWT", "chave_secreta_para_testes")
    mocker.patch("app.core.security.settings.TEMPO_EXPIRACAO_TOKEN_MINUTOS", 15)

    email_teste = "teste@exemplo.com"
    token = security.gerar_token(email=email_teste)

    payload = jwt.decode(
        token, 
        "chave_secreta_para_testes", 
        algorithms=[security.ALGORITHM]
    )

    assert payload.get("sub") == email_teste
    assert "exp" in payload
