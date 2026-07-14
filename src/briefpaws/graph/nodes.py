"""图节点实现 — Supervisor / Data / Analyst / Report。"""

from __future__ import annotations

from briefpaws.brief_logic import analyst_sections, build_plan, collect_symbol_data
from briefpaws.graph.state import ResearchState
from briefpaws.observability.langfuse_tracer import node_span
from briefpaws.report import render_report
from briefpaws.schemas.run import RunDocument, RunMeta
from briefpaws.storage.runs import new_run_id


def supervisor_node(state: ResearchState) -> dict:
    with node_span("supervisor"):
        profile = state["profile"]
        focus = state.get("focus")
        question = state.get("question")
        theme = state.get("theme")

        variant = "pre_market_brief"
        if profile == "pm" and state.get("question"):
            variant = "pm_memo"
        elif profile == "quant" and focus == "event":
            variant = "event_deep"
        elif profile == "quant" and focus == "risk":
            variant = "risk_only"
        elif theme:
            variant = f"quant_{theme}"

        run_id = new_run_id()
        plan = build_plan(profile, focus, question, plan_variant=variant)
        for step in plan.steps:
            if step.step_id == "supervisor.plan":
                step.status = "done"
        meta = RunMeta(
            run_id=run_id,
            profile=profile,
            symbols=[s.upper() for s in state["symbols"]],
            range=state.get("range_str", "3M"),
            plan_variant=variant,
            question=question,
        )
        doc = RunDocument(meta=meta, plan=plan)
        return {"doc": doc}


def data_node(state: ResearchState) -> dict:
    with node_span("data"):
        doc: RunDocument = state["doc"]
        profile = state["profile"]
        range_str = state.get("range_str", "3M")

        for step in doc.plan.steps:
            if step.step_id == "data.collect":
                step.status = "running"

        all_tools: list = []
        overview = doc.overview
        symbol_results = []
        tool_retries: list[int] = []

        for sym in doc.meta.symbols:
            sr, sym_tools = collect_symbol_data(
                sym, range_str, profile, tool_retries=tool_retries
            )
            symbol_results.append(sr)
            all_tools.extend(sym_tools)
            if sr.status == "failed" and sr.error_code == "INVALID_SYMBOL":
                doc.meta.status = "degraded"
                overview.pending_verification.append(f"{sym}: 无效代码")
            if sr.indicators and sr.indicators.mdd_3m is not None and sr.indicators.mdd_3m < -0.15:
                overview.top_risks.append(f"{sym} 3M MDD {sr.indicators.mdd_3m:.1%}")
            for n in sr.news[:1]:
                overview.top_events.append(f"{sym}: {n.title}")
            if sr.evidence_gaps:
                overview.pending_verification.append(f"{sym}: {', '.join(sr.evidence_gaps)}")

        ok_count = sum(1 for s in symbol_results if s.status == "ok")
        if ok_count == 0:
            doc.meta.status = "failed"
            doc.meta.error_code = "ALL_SYMBOLS_FAILED"
        elif ok_count < len(doc.meta.symbols):
            doc.meta.status = "degraded"
            doc.meta.degraded = True

        doc.tools = all_tools
        doc.symbols = symbol_results
        doc.overview = overview
        doc.meta.tool_retries += len(tool_retries)

        for step in doc.plan.steps:
            if step.step_id == "data.collect":
                step.status = "done"
        return {"doc": doc}


def analyst_node(state: ResearchState) -> dict:
    with node_span("analyst"):
        doc: RunDocument = state["doc"]
        for step in doc.plan.steps:
            if step.step_id == "analyst.compute":
                step.status = "running"
        sections, extra_tools = analyst_sections(doc)
        doc.tools.extend(extra_tools)
        for step in doc.plan.steps:
            if step.step_id == "analyst.compute":
                step.status = "done"
        return {"sections": sections, "doc": doc}


def report_node(state: ResearchState) -> dict:
    with node_span("report"):
        doc: RunDocument = state["doc"]
        sections = state.get("sections")
        if sections is None:
            sections, extra = analyst_sections(doc)
            doc.tools.extend(extra)
        for step in doc.plan.steps:
            if step.step_id == "report.render":
                step.status = "running"
        report_md = render_report(doc, sections=sections)
        for step in doc.plan.steps:
            if step.step_id == "report.render":
                step.status = "done"
        return {"report_md": report_md, "doc": doc}
