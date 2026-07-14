"""单轮规则反思 + pm 假设验证。"""

from __future__ import annotations

from briefpaws.config import EVIDENCE_INSUFFICIENT_PM
from briefpaws.observability.langfuse_tracer import reflection_event
from briefpaws.schemas.run import (
    HypothesisVerification,
    ReflectionCheck,
    ReflectionDecision,
    ReflectionResult,
    RunDocument,
)

_DEFINITIVE_WORDS = ("必然", "一定", "确定会", "肯定会", "毫无疑问")


def verify_pm_hypothesis(doc: RunDocument) -> HypothesisVerification | None:
    if doc.meta.profile != "pm" or not doc.meta.question:
        return None

    q = doc.meta.question
    filing_hits = 0
    total_news = 0
    for sr in doc.symbols:
        if sr.status != "ok":
            continue
        total_news += len(sr.news)
        filing_hits += sum(
            1 for n in sr.news if n.evidence_level in ("filing", "official")
        )

    asks_disclosure = any(k in q for k in ("披露", "公告", "8-K", " filing", "财报"))

    if asks_disclosure:
        if filing_hits > 0:
            return HypothesisVerification(
                question=q,
                verdict="supported",
                rationale=f"检索到 {filing_hits} 条 filing/official 来源，与「披露」类问题部分吻合。",
            )
        if total_news > 0:
            return HypothesisVerification(
                question=q,
                verdict="inconclusive",
                rationale="有新闻但无 filing/official 等级，不足以确认正式披露。",
            )
        return HypothesisVerification(
            question=q,
            verdict="unsupported",
            rationale="隔夜窗内无新闻；无法支持披露相关假设。",
        )

    sig_gap = any(
        sr.indicators and sr.indicators.overnight_gap_significant
        for sr in doc.symbols
        if sr.status == "ok"
    )
    if sig_gap and total_news == 0:
        return HypothesisVerification(
            question=q,
            verdict="inconclusive",
            rationale="存在显著跳空但无新闻证据，假设无法验证。",
        )
    return HypothesisVerification(
        question=q,
        verdict="inconclusive",
        rationale="已收集量价与新闻；需 PM 进一步判断。",
    )


def _pick_decision(doc: RunDocument, checks: list[ReflectionCheck], passed: bool) -> ReflectionDecision:
    if passed:
        return "pass"
    return "downgrade"


def _apply_downgrade(doc: RunDocument, checks: list[ReflectionCheck]) -> None:
    failed = [c.name for c in checks if not c.passed]
    doc.meta.status = "degraded"
    doc.meta.degraded = True
    doc.meta.degraded_reason = f"Reflection 未通过: {', '.join(failed)}"


def run_reflection(doc: RunDocument, sections: dict) -> ReflectionResult:
    checks: list[ReflectionCheck] = []

    done_ids = {s.step_id for s in doc.plan.steps if s.status == "done"}
    pre_report = {"supervisor.plan", "data.collect", "analyst.compute"}
    all_four = {"supervisor.plan", "data.collect", "analyst.compute", "report.render"}
    if all_four.issubset(done_ids):
        plan_ok, plan_detail = True, "4/4 steps done"
    else:
        plan_ok = pre_report.issubset(done_ids)
        plan_detail = f"{len(done_ids)}/4 steps done (pre-report)"

    checks.append(
        ReflectionCheck(name="plan_steps_done", passed=plan_ok, detail=plan_detail)
    )

    if doc.meta.profile == "pm":
        report_text = _sections_text(sections)
        for sr in doc.symbols:
            if not sr.news and "pm_attribution" in sr.evidence_gaps:
                ok = EVIDENCE_INSUFFICIENT_PM in report_text
                checks.append(
                    ReflectionCheck(
                        name=f"pm_evidence_guard_{sr.symbol}",
                        passed=ok,
                        detail="无新闻时需证据不足句式",
                    )
                )
        for sr in doc.symbols:
            official = any(n.evidence_level in ("filing", "official") for n in sr.news)
            if not official:
                sym_sec = next(
                    (s for s in sections.get("symbols", []) if s.get("symbol") == sr.symbol),
                    {},
                )
                core = sym_sec.get("core_view") or ""
                bad = any(w in core for w in _DEFINITIVE_WORDS)
                checks.append(
                    ReflectionCheck(
                        name=f"no_definitive_without_official_{sr.symbol}",
                        passed=not bad,
                        detail="无 official 新闻时核心观点避免确定性措辞",
                    )
                )

    passed = all(c.passed for c in checks)
    decision = _pick_decision(doc, checks, passed)
    if decision == "downgrade":
        _apply_downgrade(doc, checks)

    reflection_event(decision)
    return ReflectionResult(passed=passed, checks=checks, decision=decision)


def strip_definitive_wording(text: str) -> str:
    out = text
    for w in _DEFINITIVE_WORDS:
        out = out.replace(w, "")
    out = out.strip()
    return out or "暂无高置信结论（需更多官方/披露证据）"


def _sections_text(sections: dict) -> str:
    parts: list[str] = []
    for s in sections.get("symbols", []):
        for key in ("core_view", "move_attribution", "one_line", "events"):
            val = s.get(key)
            if isinstance(val, list):
                parts.extend(str(x) for x in val)
            elif val:
                parts.append(str(val))
    return "\n".join(parts)
