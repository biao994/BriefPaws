"""BriefPaws 研究简报的 LangGraph 状态。"""

from __future__ import annotations

from typing import TypedDict

from briefpaws.schemas.run import RunDocument


class ResearchState(TypedDict, total=False):
    symbols: list[str]
    range_str: str
    profile: str
    focus: str | None
    question: str | None
    theme: str | None
    doc: RunDocument
    sections: dict
    report_md: str
