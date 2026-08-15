import logging
import time

from langchain_ollama import ChatOllama

from app.core.config import settings
from app.core.request_context import count_one
from app.services.log_service import describe_value, log_event

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
    wanted_shape = answer_schema.__name__

    log_event(
        "llm",
        "llm_call_started",
        details={
            "model": settings.ollama_model,
            "wanted_shape": wanted_shape,
            "prompt_chars": len(prompt),
            "prompt": prompt if settings.log_full_payloads else None,
        },
    )

    for try_number in range(1, HOW_MANY_TRIES + 1):
        started_at = time.perf_counter()
        answer = llm.invoke(prompt)
        duration_ms = round((time.perf_counter() - started_at) * 1000)

        if answer is not None:
            count_one("llm_calls")
            log_event(
                "llm",
                "llm_call_finished",
                details={
                    "wanted_shape": wanted_shape,
                    "try_number": try_number,
                    "answer": describe_value(answer),
                },
                duration_ms=duration_ms,
            )
            return answer

        # The model answered with no tool call at all, so we try again.
        count_one("llm_retries")
        log_event(
            "llm",
            "llm_call_retried",
            details={"wanted_shape": wanted_shape, "try_number": try_number},
            duration_ms=duration_ms,
            level=logging.WARNING,
        )

    message = (
        f"The model did not answer with a {wanted_shape} after {HOW_MANY_TRIES} tries. "
        f"Try again, or use a bigger model."
    )
    log_event("llm", "llm_call_failed", error=message, level=logging.ERROR)
    raise ValueError(message)
