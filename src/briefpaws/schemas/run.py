"""run.json 契约 — L0b 第 2 步（plan.steps，尚无 reflection）。"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolRecord(BaseModel):
    name: str
    status: Literal["ok", "error", "skipped"] = "ok"
    error: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)


class NewsItem(BaseModel):
    title: str
    url: str
    time: str
    source: str
    evidence_level: Literal["filing", "official", "aggregator", "unknown"] = "unknown"
    summary: str | None = None


class Indicators(BaseModel):
    return_3m: float | None = None
    vol_20d_ann: float | None = None
    mdd_3m: float | None = None
    overnight_gap: float | None = None
    overnight_gap_significant: bool = False
    volume_ratio_20d: float | None = None
    volume_flag: Literal["spike", "dry", "normal", "unknown"] = "unknown"
    worst_1d_return_20d: float | None = None


class Trigger(BaseModel):
    text: str
    evidence: str


class SymbolResult(BaseModel):
    symbol: str
    status: Literal["ok", "failed", "skipped"] = "ok"
    error_code: str | None = None
    skipped_sections: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    indicators: Indicators | None = None
    news: list[NewsItem] = Field(default_factory=list)
    triggers: list[Trigger] = Field(default_factory=list)
    one_line_conclusion: str | None = None
    watchlist: list[str] = Field(default_factory=list)


class RunMeta(BaseModel):
    run_id: str
    profile: Literal["quant", "pm"] = "pm"
    symbols: list[str]
    range: str = "3M"
    timezone: str = "Asia/Shanghai"
    plan_variant: str = "pre_market_brief"
    status: Literal["completed", "failed", "degraded"] = "completed"
    error_code: str | None = None
    skipped_sections: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    degraded: bool = False
    tool_retries: int = 0
    llm_retries: int = 0


class OverviewBlock(BaseModel):
    top_risks: list[str] = Field(default_factory=list)
    top_events: list[str] = Field(default_factory=list)
    pending_verification: list[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    step_id: str
    target_agent: Literal["supervisor", "data", "analyst", "report"] = "data"
    tool_hint: str | None = None
    status: Literal["pending", "running", "done", "skipped"] = "pending"


class RunPlan(BaseModel):
    steps: list[PlanStep] = Field(default_factory=list)


class RunDocument(BaseModel):
    meta: RunMeta
    plan: RunPlan = Field(default_factory=RunPlan)
    tools: list[ToolRecord] = Field(default_factory=list)
    symbols: list[SymbolResult] = Field(default_factory=list)
    overview: OverviewBlock = Field(default_factory=OverviewBlock)
