"""简报共用逻辑：工具、计划、分析师章节（不依赖 graph）。"""

from __future__ import annotations

from briefpaws.config import EVIDENCE_INSUFFICIENT_PM
from briefpaws.observability.langfuse_tracer import tool_span
from briefpaws.schemas.run import (
    PlanStep,
    RunDocument,
    RunPlan,
    SymbolResult,
    ToolRecord,
)
from briefpaws.tools.indicators import compute_indicators
from briefpaws.tools.news import get_latest_news
from briefpaws.tools.price import get_price_series
from briefpaws.triggers import build_triggers


def build_plan(
    profile: str,
    focus: str | None = None,
    question: str | None = None,
    *,
    plan_variant: str = "pre_market_brief",
) -> RunPlan:
    analyst_hint = "build_triggers, overview aggregation"
    if profile == "quant" and focus == "risk":
        analyst_hint = "risk-focused triggers + overview"
    return RunPlan(
        steps=[
            PlanStep(
                step_id="supervisor.plan",
                target_agent="supervisor",
                tool_hint="plan_variant",
                status="pending",
            ),
            PlanStep(
                step_id="data.collect",
                target_agent="data",
                tool_hint="get_price_series, compute_indicators, get_latest_news",
                status="pending",
            ),
            PlanStep(
                step_id="analyst.compute",
                target_agent="analyst",
                tool_hint=analyst_hint,
                status="pending",
            ),
            PlanStep(
                step_id="report.render",
                target_agent="report",
                tool_hint="report template",
                status="pending",
            ),
        ]
    )


def collect_symbol_data(
    symbol: str, range_str: str, profile: str, *, tool_retries: list[int] | None = None
) -> tuple[SymbolResult, list[ToolRecord]]:
    retries_ref = tool_retries if tool_retries is not None else []
    tools: list[ToolRecord] = []
    result = SymbolResult(symbol=symbol.upper())

    with tool_span("get_price_series"):
        price = get_price_series(symbol, range_str)
    if not price.ok and price.error_code not in ("INVALID_SYMBOL",):
        retries_ref.append(1)
        with tool_span("get_price_series"):
            price = get_price_series(symbol, range_str)
    tools.append(
        ToolRecord(
            name="get_price_series",
            status="ok" if price.ok else "error",
            error=price.error_code,
            input={"symbol": symbol, "range": range_str},
            output={"rows": len(price.frame) if price.frame is not None else 0},
        )
    )

    if price.error_code == "INVALID_SYMBOL":
        result.status = "failed"
        result.error_code = "INVALID_SYMBOL"
        return result, tools

    if not price.ok or price.frame is None:
        result.status = "skipped"
        result.error_code = "DATA_EMPTY"
        result.skipped_sections.extend(["snapshot", "triggers"])
        result.evidence_gaps.append("price_data")
        return result, tools

    with tool_span("compute_indicators"):
        ind = compute_indicators(price.frame)
    result.indicators = ind
    tools.append(
        ToolRecord(
            name="compute_indicators",
            status="ok",
            input={"symbol": symbol},
            output=ind.model_dump(),
        )
    )

    with tool_span("get_latest_news"):
        news = get_latest_news(symbol)
    result.news = news
    tools.append(
        ToolRecord(
            name="get_latest_news",
            status="ok",
            input={"symbol": symbol},
            output={"count": len(news)},
        )
    )

    result.triggers = build_triggers(ind, news)
    high = [n for n in news if n.evidence_level in ("filing", "official")]
    result.one_line_conclusion = high[0].title if high else None
    if profile == "pm" and not news:
        result.evidence_gaps.append("pm_attribution")

    watch: list[str] = []
    if ind.overnight_gap_significant:
        watch.append("显著隔夜跳空")
    if ind.volume_flag == "spike":
        watch.append("显著放量")
    if not news:
        watch.append("待核实：隔夜新闻不足")
    result.watchlist = watch[:3]
    return result, tools


def _fmt_pct(x: float | None) -> str:
    return "N/A" if x is None else f"{x:.2%}"


def _symbol_snapshot_lines(sr: SymbolResult) -> list[str]:
    ind = sr.indicators
    if not ind:
        return ["行情数据缺失"]
    return [
        f"3M收益: {_fmt_pct(ind.return_3m)}",
        f"20D年化波动: {_fmt_pct(ind.vol_20d_ann)}",
        f"3M最大回撤: {_fmt_pct(ind.mdd_3m)}",
        f"隔夜跳空: {_fmt_pct(ind.overnight_gap)}"
        + (" [显著]" if ind.overnight_gap_significant else ""),
        f"成交量/20D均值: {ind.volume_ratio_20d:.2f}x ({ind.volume_flag})"
        if ind.volume_ratio_20d
        else "成交量: N/A",
        f"近20D最差单日: {_fmt_pct(ind.worst_1d_return_20d)}",
    ]


def analyst_sections(doc: RunDocument) -> tuple[dict, list[ToolRecord]]:
    sections: dict = {
        "overview": doc.overview.model_dump(),
        "symbols": [],
    }
    for sr in doc.symbols:
        events = [f"{n.title} [{n.source}] {n.time} {n.url}" for n in sr.news[:3]]
        if not events and doc.meta.profile == "pm":
            events = [EVIDENCE_INSUFFICIENT_PM]
        sections["symbols"].append(
            {
                "symbol": sr.symbol,
                "one_line": sr.one_line_conclusion or "暂无高置信结论",
                "snapshot": _symbol_snapshot_lines(sr)[:6],
                "events": events[:3],
                "watchlist": sr.watchlist[:3],
                "triggers": [t.text + f"（证据：{t.evidence}）" for t in sr.triggers[:2]],
                "gaps": sr.evidence_gaps[:2] or ["无"],
            }
        )
    return sections, []
