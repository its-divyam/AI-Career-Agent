from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Skillgraph"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./career_agent.db"

    JWT_SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3.2"
    LLM_BASE_URL: str = "http://localhost:11434"

    REDIS_URL: str = "redis://localhost:6379/0"

    CHROMA_PERSIST_DIR: str = "./data/chroma"

    EMBED_MODEL: str = "nomic-embed-text"
    RAG_TOP_K: int = 4

    MAX_UPLOAD_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
