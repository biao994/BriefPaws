"""PM 备忘录模式 — question 出现在报告备忘录章节中。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_PY = ROOT / "run.py"


def test_pm_memo_question_in_report(tmp_path: Path) -> None:
    question = "隔夜是否有影响开盘的披露？"
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
            question,
            "--out",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode in (0, 1), proc.stderr + proc.stdout
    run_dir = next(out.iterdir())
    data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    report = (run_dir / "report.md").read_text(encoding="utf-8")

    assert data["meta"]["plan_variant"] == "pm_memo"
    assert data["meta"]["question"] == question
    assert question in report
    assert "核心观点" in report
    assert "催化剂" in report
    assert "异动与归因" in report
    assert "证据与局限" in report
