"""LangGraph StateGraph — Supervisor → Data → Analyst → Report（线性）。"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from briefpaws.graph.nodes import analyst_node, data_node, report_node, supervisor_node
from briefpaws.graph.state import ResearchState


def build_research_graph():
    g = StateGraph(ResearchState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("data", data_node)
    g.add_node("analyst", analyst_node)
    g.add_node("report", report_node)

    g.add_edge(START, "supervisor")
    g.add_edge("supervisor", "data")
    g.add_edge("data", "analyst")
    g.add_edge("analyst", "report")
    g.add_edge("report", END)
    return g.compile()


def invoke_research_graph(
    symbols: list[str],
    *,
    range_str: str = "3M",
    profile: str = "pm",
    focus: str | None = None,
    question: str | None = None,
    theme: str | None = None,
) -> ResearchState:
    graph = build_research_graph()
    initial: ResearchState = {
        "symbols": symbols,
        "range_str": range_str,
        "profile": profile,
        "focus": focus,
        "question": question,
        "theme": theme,
    }
    return graph.invoke(initial)
