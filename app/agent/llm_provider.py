from langchain_ollama import ChatOllama

from app.core.config import settings


def get_llm() -> ChatOllama:
    """Create the local Ollama model that every node uses."""
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.llm_temperature,
    )
