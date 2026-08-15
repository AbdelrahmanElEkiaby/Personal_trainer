from langchain_ollama import ChatOllama

from app.core.config import settings

# A small local model sometimes answers with nothing, so we ask again before we fail.
HOW_MANY_TRIES = 3


def get_llm() -> ChatOllama:
    """Create the local Ollama model that every node uses."""
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.llm_temperature,
    )


def ask_model_for(answer_schema, prompt: str):
    """Ask the model to answer with the shape of answer_schema.

    The model sometimes gives back nothing at all. When that happens we simply ask
    again, and only after a few tries we say it failed.
    """
    llm = get_llm().with_structured_output(answer_schema)

    for _ in range(HOW_MANY_TRIES):
        answer = llm.invoke(prompt)
        if answer is not None:
            return answer

    raise ValueError(
        f"The model did not answer with a {answer_schema.__name__} after "
        f"{HOW_MANY_TRIES} tries. Try again, or use a bigger model."
    )
