from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    USUARIO_BD: str
    SENHA_BD: str
    NOME_BD: str
    HOST_BD: str
    PORTA_BD: str

    TITULO_API: str
    URL_BASE_API_PRODUTO: str

    CHAVE_SEGURANCA_JWT: str
    TEMPO_EXPIRACAO_TOKEN_MINUTOS: int

    @property
    def url_bd(self) -> str:
        return f"postgresql+asyncpg://{self.USUARIO_BD}:{self.SENHA_BD}@{self.HOST_BD}:{self.PORTA_BD}/{self.NOME_BD}"

settings = Settings()
