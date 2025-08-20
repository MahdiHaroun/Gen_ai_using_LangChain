from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_password: str = ""
    database_name: str = "chat_db"
    database_username: str = "user"
    LANGSMITH_TRACING: str = "false"
    LANGSMITH_ENDPOINT: str = ""
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = ""
    OPENAI_API_KEY: str = ""
    HF_Token: str = ""
    GROQ_API: str = ""

    class Config:
        env_file = "backend/.env"


settings = Settings()
