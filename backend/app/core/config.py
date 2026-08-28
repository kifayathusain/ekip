from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ekip:ekip@localhost:5432/ekip"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    llm_provider: str = "mock"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
