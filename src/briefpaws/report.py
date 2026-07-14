"""从 Jinja2 模板渲染 report.md。"""

from __future__ import annotations

from jinja2 import Environment, FileSystemLoader, select_autoescape

from briefpaws.config import EVIDENCE_INSUFFICIENT_PM, TEMPLATES_DIR
from briefpaws.schemas.run import RunDocument, SymbolResult


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
        f"隔夜跳空: {_fmt_pct(ind.overnight_gap)}" + (" [显著]" if ind.overnight_gap_significant else ""),
        f"成交量/20D均值: {ind.volume_ratio_20d:.2f}x ({ind.volume_flag})"
        if ind.volume_ratio_20d
        else "成交量: N/A",
        f"近20D最差单日: {_fmt_pct(ind.worst_1d_return_20d)}",
    ]


def build_sections(doc: RunDocument) -> dict:
    symbols = []
    for sr in doc.symbols:
        events = [f"{n.title} [{n.source}] {n.time} {n.url}" for n in sr.news[:3]]
        if not events and doc.meta.profile == "pm":
            events = [EVIDENCE_INSUFFICIENT_PM]
        symbols.append(
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
    return {"overview": doc.overview.model_dump(), "symbols": symbols}


def render_report(doc: RunDocument, *, sections: dict | None = None) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(disabled_extensions=()),
    )
    template_name = "report_pre_market.md.j2"
    if doc.meta.profile == "quant":
        template_name = "report_quant.md.j2"
    elif doc.meta.profile == "pm" and doc.meta.plan_variant == "pm_memo":
        template_name = "report_pm.md.j2"
    if sections is None:
        from briefpaws.brief_logic import analyst_sections
        sections, _ = analyst_sections(doc)
    tpl = env.get_template(template_name)
    return tpl.render(meta=doc.meta.model_dump(), sections=sections)
