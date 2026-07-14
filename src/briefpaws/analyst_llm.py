"""LLM 增强 Analyst：pm core_view，带引用约束。"""

from __future__ import annotations

import json

from briefpaws.llm_client import chat_json, llm_enabled
from briefpaws.schemas.run import RunDocument, SymbolResult

_PM_SYSTEM = """你是买方投研 PM 助手。只能根据用户提供的 JSON 事实写「核心观点」。
规则：
1. 不得编造数字、事件、URL；JSON 里没有的不要写。
2. 若无 filing/official 新闻，必须说明证据不足，不得确定性归因。
3. 输出严格 JSON：{"core_view": "一句话，≤80字"}"""


def enhance_pm_core_view(
    sr: SymbolResult, doc: RunDocument
) -> tuple[str | None, str | None]:
    if not llm_enabled():
        return None, "LLM_DISABLED"
    if doc.meta.plan_variant != "pm_memo":
        return None, "NOT_PM_MEMO"

    payload = {
        "symbol": sr.symbol,
        "question": doc.meta.question,
        "indicators": sr.indicators.model_dump() if sr.indicators else None,
        "news": [n.model_dump() for n in sr.news[:3]],
        "evidence_gaps": sr.evidence_gaps,
        "rule_core_view": sr.one_line_conclusion,
    }
    user = f"事实 JSON：\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    data, err = chat_json(system=_PM_SYSTEM, user=user)
    if err or not data:
        return None, err or "NO_DATA"
    core = (data.get("core_view") or "").strip()
    if not core:
        return None, "EMPTY_CORE_VIEW"
    return core[:200], None
