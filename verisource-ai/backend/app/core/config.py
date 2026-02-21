from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    # App
    APP_NAME: str = "VeriSource AI"
    DEBUG: bool = True
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Groq LLM
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()