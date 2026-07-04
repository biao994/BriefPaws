"""Langfuse 追踪 — 未配置密钥时为 no-op。"""

from __future__ import annotations

import contextvars
import os
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, TypeVar

T = TypeVar("T")

_active_trace: contextvars.ContextVar[Any | None] = contextvars.ContextVar(
    "briefpaws_langfuse_trace", default=None
)


def _langfuse_enabled() -> bool:
    return bool(os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"))


def _get_client():
    from langfuse import Langfuse

    host = os.environ.get("LANGFUSE_HOST", "").strip() or None
    return Langfuse(host=host) if host else Langfuse()


@contextmanager
def tool_span(name: str) -> Generator[None, None, None]:
    with node_span(f"tool.{name}"):
        yield


@contextmanager
def node_span(name: str) -> Generator[None, None, None]:
    trace = _active_trace.get()
    if trace is None:
        yield
        return
    span = trace.span(name=f"node.{name}")
    try:
        yield
    finally:
        span.end()


def trace_brief_run(
    *,
    symbols: list[str],
    profile: str,
    range_str: str,
    execute: Callable[[], T],
) -> T:
    if not _langfuse_enabled():
        return execute()

    client = _get_client()
    trace = client.trace(
        name="briefpaws_research",
        metadata={"symbols": symbols, "profile": profile, "range": range_str},
    )
    token = _active_trace.set(trace)
    try:
        result = execute()
        if isinstance(result, tuple) and len(result) >= 1:
            doc = result[0]
            if hasattr(doc, "meta"):
                trace.update(output={"run_id": doc.meta.run_id, "status": doc.meta.status})
        return result
    except Exception as exc:
        trace.update(output={"status": "error", "error": str(exc)})
        raise
    finally:
        _active_trace.reset(token)
        client.flush()
