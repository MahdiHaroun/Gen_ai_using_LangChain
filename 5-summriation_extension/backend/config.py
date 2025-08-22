from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LANGSMITH_TRACING: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str
    GROQ_API: str

    class Config:
        env_file = "backend/.env"


settings = Settings()