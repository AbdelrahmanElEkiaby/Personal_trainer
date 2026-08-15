"""Creates the model every node uses.

This is the only file that knows which company answers our questions. Everything
else asks for "the model" and does not care. To change provider, change
LLM_PROVIDER in the .env file.
"""

import logging
import time

from app.core.config import settings
from app.core.request_context import count_one
from app.observability.logger import describe_value, log_event, remember_tokens

# A model sometimes answers with nothing, so we ask again before we fail.
HOW_MANY_TRIES = 3

OPENAI = "openai"
OLLAMA = "ollama"


def get_active_model_name() -> str:
    """The model we are really talking to right now."""
    if settings.llm_provider == OPENAI:
        return settings.openai_model
    return settings.ollama_model


def get_llm():
    """Create the model that every node uses."""
    if settings.llm_provider == OPENAI:
        # Imported here so the app still starts when the OpenAI package is not
        # installed and we only want to use Ollama.
        from langchain_openai import ChatOpenAI

        if not settings.openai_api_key:
            raise ValueError(
                "No OpenAI key. Put OPENAI_API_KEY in the .env file, or set "
                "LLM_PROVIDER=ollama to use the local model."
            )

        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.llm_temperature,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.llm_temperature,
        # num_ctx only exists for Ollama, OpenAI would refuse it.
        num_ctx=settings.ollama_context_size,
    )


def ask_model_for(answer_schema, prompt: str):
    """Ask the model to answer with the shape of answer_schema.

    We ask for the raw answer too, because that is where the token counts are,
    and because it tells us why an answer did not fit the shape.
    """
    llm = get_llm().with_structured_output(answer_schema, include_raw=True)
    wanted_shape = answer_schema.__name__

    log_event(
        "llm",
        "llm_call_started",
        details={
            "provider": settings.llm_provider,
            "model": get_active_model_name(),
            "wanted_shape": wanted_shape,
            "prompt_chars": len(prompt),
            "prompt": prompt if settings.log_full_payloads else None,
        },
    )

    for try_number in range(1, HOW_MANY_TRIES + 1):
        started_at = time.perf_counter()
        answer = llm.invoke(prompt)
        duration_ms = round((time.perf_counter() - started_at) * 1000)

        parsed_answer = answer.get("parsed")
        tokens = remember_tokens(answer.get("raw"))

        if parsed_answer is not None:
            count_one("llm_calls")
            log_event(
                "llm",
                "llm_call_finished",
                details={
                    "wanted_shape": wanted_shape,
                    "try_number": try_number,
                    "tokens": tokens,
                    "answer": describe_value(parsed_answer),
                },
                duration_ms=duration_ms,
            )
            return parsed_answer

        # The answer did not fit the shape, so we try again.
        count_one("llm_retries")
        why_it_failed = answer.get("parsing_error")
        log_event(
            "llm",
            "llm_call_retried",
            details={"wanted_shape": wanted_shape, "try_number": try_number},
            duration_ms=duration_ms,
            error=str(why_it_failed) if why_it_failed else None,
            level=logging.WARNING,
        )

    message = (
        f"The model did not answer with a {wanted_shape} after {HOW_MANY_TRIES} tries. "
        f"Try again, or use a stronger model."
    )
    log_event("llm", "llm_call_failed", error=message, level=logging.ERROR)
    raise ValueError(message)
