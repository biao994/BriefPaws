"""Reflection 与假设验证测试。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from briefpaws.reflection import run_reflection, verify_pm_hypothesis
from briefpaws.schemas.run import Indicators, NewsItem, RunDocument, RunMeta, SymbolResult

ROOT = Path(__file__).resolve().parents[1]
RUN_PY = ROOT / "run.py"


def _doc_with_news() -> RunDocument:
    meta = RunMeta(
        run_id="test",
        profile="pm",
        symbols=["AAPL"],
        plan_variant="pm_memo",
        question="隔夜是否有影响开盘的披露？",
    )
    sr = SymbolResult(
        symbol="AAPL",
        indicators=Indicators(return_3m=0.1),
        news=[
            NewsItem(
                title="8-K filed",
                url="https://sec.gov/",
                time="2026-06-04T22:00:00+00:00",
                source="sec",
                evidence_level="filing",
            )
        ],
    )
    from briefpaws.brief_logic import build_plan

    return RunDocument(meta=meta, plan=build_plan("pm", question=meta.question), symbols=[sr])


def test_hypothesis_supported_when_filing_news() -> None:
    h = verify_pm_hypothesis(_doc_with_news())
    assert h is not None
    assert h.verdict == "supported"


def test_reflection_passes_with_evidence_phrase() -> None:
    doc = _doc_with_news()
    doc.symbols[0].news = []
    doc.symbols[0].evidence_gaps.append("pm_attribution")
    sections = {
        "symbols": [
            {
                "symbol": "AAPL",
                "core_view": "暂无",
                "move_attribution": [
                    "当前检索范围内未发现足够新闻/公告证据，以下归因仅作假设性讨论，不构成投资结论。"
                ],
            }
        ]
    }
    for s in doc.plan.steps:
        s.status = "done"
    r = run_reflection(doc, sections)
    assert r.passed
    assert r.decision == "pass"


def test_run_json_has_hypothesis_and_reflection(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    proc = subprocess.run(
        [
            sys.executable,
            str(RUN_PY),
            "--symbols",
            "AAPL",
            "--profile",
            "pm",
            "--question",
            "隔夜是否有影响开盘的披露？",
            "--out",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode in (0, 1), proc.stderr + proc.stdout
    data = json.loads((next(out.iterdir()) / "run.json").read_text(encoding="utf-8"))
    assert data["hypothesis"] is not None
    assert data["reflection"] is not None
