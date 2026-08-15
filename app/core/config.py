from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings are read from the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Which model we talk to: "openai" or "ollama".
    # Everything else in the app is the same, only this line changes.
    llm_provider: str = "openai"

    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    # Prices change often, so they are read from the .env and never hardcoded.
    # Leave them at 0 and we simply do not estimate the cost.
    openai_input_price_per_million: float = 0.0
    openai_output_price_per_million: float = 0.0

    # Ollama settings
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.2
    # Ollama only remembers 2048 tokens by default, which is too small once the
    # model starts reading tool answers, so we give it more.
    ollama_context_size: int = 8192
    # How many times the model can ask for tools before we stop it.
    max_tool_turns: int = 5

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

    # Logging settings
    log_level: str = "INFO"
    # Every run writes its own file in here, named after the time it started.
    log_folder: str = "logs"
    log_to_console: bool = True
    # Writes the full prompts and the full plans. Very useful to find a problem,
    # but it makes the log file grow fast.
    log_full_payloads: bool = True
    # The profile has the age, the weight and the medical conditions, so turn
    # this off if these should not be written in a file.
    log_user_details: bool = True

    # API settings
    app_name: str = "Personal Trainer Agent"
    app_version: str = "1.0.0"


settings = Settings()
