from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings are read from the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ollama settings
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.3

    # USDA FoodData Central settings.
    # DEMO_KEY works for a few requests per hour, get a free key from
    # https://fdc.nal.usda.gov/api-key-signup.html
    usda_api_key: str = "DEMO_KEY"
    usda_base_url: str = "https://api.nal.usda.gov/fdc/v1"
    usda_timeout_seconds: int = 30

    # ExerciseDB settings.
    # This is the free and open host, it needs no key and it holds 1500 exercises.
    exercisedb_base_url: str = "https://oss.exercisedb.dev/api/v1"
    exercisedb_timeout_seconds: int = 30

    # API settings
    app_name: str = "Personal Trainer Agent"
    app_version: str = "1.0.0"


settings = Settings()
