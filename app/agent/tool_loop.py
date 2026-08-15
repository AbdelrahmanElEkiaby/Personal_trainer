"""Lets the model call the tools by itself, until it has the facts it needs.

The model answers with a list of tool calls, we run them, we give the answers
back, and we repeat. When the model stops asking for tools, it is done.

We stop after a few turns anyway, because a small model can ask for tools forever.
"""

import json
import logging
import time

from langchain_core.messages import HumanMessage, ToolMessage

from app.agent.llm_provider import get_llm
from app.core.config import settings
from app.observability.logger import log_event, remember_tokens

# One tool answer can be long, and the model has a limited memory, so we cut it.
BIGGEST_TOOL_ANSWER_CHARS = 1500


def collect_facts_with_tools(tools: list, prompt: str, step_name: str) -> list[dict]:
    """Give the tools to the model and let it use them. Returns what it found."""
    tools_by_name = {tool.name: tool for tool in tools}
    llm_with_tools = get_llm().bind_tools(tools)

    messages = [HumanMessage(content=prompt)]
    facts_found = []

    for turn_number in range(1, settings.max_tool_turns + 1):
        started_at = time.perf_counter()
        answer = llm_with_tools.invoke(messages)
        messages.append(answer)
        tokens = remember_tokens(answer)

        if not answer.tool_calls:
            log_event(
                step_name,
                "tool_loop_finished",
                details={
                    "turns_used": turn_number,
                    "facts_found": len(facts_found),
                    "tokens": tokens,
                },
                duration_ms=round((time.perf_counter() - started_at) * 1000),
            )
            return facts_found

        for tool_call in answer.tool_calls:
            result = _run_one_tool(tools_by_name, tool_call, step_name)
            facts_found.append(
                {"tool": tool_call["name"], "args": tool_call["args"], "result": result}
            )
            messages.append(
                ToolMessage(
                    content=json.dumps(result, default=str)[:BIGGEST_TOOL_ANSWER_CHARS],
                    tool_call_id=tool_call["id"],
                )
            )

    log_event(
        step_name,
        "tool_loop_stopped_too_long",
        details={"turns_used": settings.max_tool_turns, "facts_found": len(facts_found)},
        level=logging.WARNING,
    )
    return facts_found


def _run_one_tool(tools_by_name: dict, tool_call: dict, step_name: str):
    """Run one tool the model asked for, and never let it break the graph."""
    tool = tools_by_name.get(tool_call["name"])
    if tool is None:
        # The model invented a tool name that does not exist.
        log_event(
            step_name,
            "tool_not_found",
            details={"asked_for": tool_call["name"]},
            level=logging.WARNING,
        )
        return {"error": f"There is no tool named '{tool_call['name']}'."}

    started_at = time.perf_counter()
    try:
        result = tool.invoke(tool_call["args"])
    except Exception as error:
        log_event(
            step_name,
            "tool_failed",
            details={"tool": tool_call["name"], "args": tool_call["args"]},
            error=f"{type(error).__name__}: {error}",
            level=logging.WARNING,
        )
        return {"error": str(error)}

    log_event(
        step_name,
        "tool_used",
        details={"tool": tool_call["name"], "args": tool_call["args"], "result": result},
        duration_ms=round((time.perf_counter() - started_at) * 1000),
    )
    return result


def write_facts_for_the_prompt(facts_found: list[dict]) -> str:
    """Turn what the tools answered into text we can put inside the next prompt."""
    if not facts_found:
        return "You found nothing with the tools, so use what you already know."

    lines = []
    for fact in facts_found:
        answer_text = json.dumps(fact["result"], default=str)[:BIGGEST_TOOL_ANSWER_CHARS]
        lines.append(f"- {fact['tool']}({json.dumps(fact['args'])}) answered: {answer_text}")
    return "\n".join(lines)
