from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentFlow"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # openai | ollama | mock
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agentflow.db"
    
    # Vector Store
    CHROMADB_DIR: str = "./chroma_db"
    CHROMADB_COLLECTION: str = "agentflow_docs"
    
    # Integrations
    SLACK_WEBHOOK_URL: str = ""
    EMAIL_SMTP_HOST: str = ""
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SENDER: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_METRICS_ENABLED: bool = True

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
