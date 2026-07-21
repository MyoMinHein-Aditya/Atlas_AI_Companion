import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Determine the directory where this script sits, to resolve root env files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    # API Keys
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")

    # Backend server settings
    backend_host: str = Field(default="127.0.0.1", validation_alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, validation_alias="BACKEND_PORT")
    python_env: str = Field(default="development", validation_alias="PYTHON_ENV")

    # PostgreSQL Database settings
    db_user: str = Field(default="postgres", validation_alias="DB_USER")
    db_password: str = Field(default="postgres", validation_alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")
    db_name: str = Field(default="atlas", validation_alias="DB_NAME")
    database_url: str = Field(default="", validation_alias="DATABASE_URL")

    # Automatically computed property for DB connection URL
    @property
    def computed_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
