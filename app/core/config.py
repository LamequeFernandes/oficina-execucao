from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    MONGODB_URL: str
    MONGODB_DATABASE: str = "oficina_execucao"
    SECRET_KEY: str
    ALGORITHM: str
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    URL_API_OS: str  # URL do microsserviço de Ordem de Serviço


settings = Settings()  # type: ignore
