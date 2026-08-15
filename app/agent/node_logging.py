"""A small decorator so every graph node is logged the same way.

Without it we would have to write the same start / finish / failed lines inside
every node, and the nodes would stop being easy to read.
"""

import functools
import logging
import time

from app.core.request_context import save_step_time
from app.observability.logger import describe_value, log_event


def log_node(step_name: str):
    """Log when a node starts, how long it took, and what it put in the state."""

    def decorate(node_function):
        @functools.wraps(node_function)
        def run_the_node_and_log_it(state):
            log_event(step_name, "node_started")
            started_at = time.perf_counter()

            try:
                answer = node_function(state)
            except Exception as error:
                log_event(
                    step_name,
                    "node_failed",
                    duration_ms=_milliseconds_since(started_at),
                    error=f"{type(error).__name__}: {error}",
                    level=logging.ERROR,
                )
                raise

            duration_ms = _milliseconds_since(started_at)
            save_step_time(step_name, duration_ms)
            log_event(
                step_name,
                "node_finished",
                details={name: describe_value(value) for name, value in answer.items()},
                duration_ms=duration_ms,
            )
            return answer

        return run_the_node_and_log_it

    return decorate


def _milliseconds_since(started_at: float) -> int:
    return round((time.perf_counter() - started_at) * 1000)
