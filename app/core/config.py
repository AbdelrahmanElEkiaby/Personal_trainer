from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings are read from the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ollama settings
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.3

    # API settings
    app_name: str = "Personal Trainer Agent"
    app_version: str = "1.0.0"


settings = Settings()
