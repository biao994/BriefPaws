"""四节点流水线 — LangGraph 编排。"""

from __future__ import annotations

from pathlib import Path

from briefpaws.graph.research_graph import invoke_research_graph
from briefpaws.observability.langfuse_tracer import trace_brief_run
from briefpaws.schemas.run import RunDocument


def run_brief(
    symbols: list[str],
    *,
    range_str: str = "3M",
    profile: str = "pm",
    timezone: str = "Asia/Shanghai",
    focus: str | None = None,
    question: str | None = None,
    theme: str | None = None,
    out_dir: Path | None = None,
) -> tuple[RunDocument, str]:
    def _execute():
        state = invoke_research_graph(
            symbols,
            range_str=range_str,
            profile=profile,
            focus=focus,
            question=question,
            theme=theme,
        )
        doc = state["doc"]
        doc.meta.timezone = timezone
        report_md = state.get("report_md") or ""
        return doc, report_md

    return trace_brief_run(
        symbols=symbols,
        profile=profile,
        range_str=range_str,
        execute=_execute,
    )
