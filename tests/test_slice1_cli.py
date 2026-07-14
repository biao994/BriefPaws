"""L0a CLI 冒烟测试。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_PY = ROOT / "run.py"


def test_cli_creates_run_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    proc = subprocess.run(
        [
            sys.executable,
            str(RUN_PY),
            "--symbols",
            "AAPL",
            "--range",
            "3M",
            "--profile",
            "pm",
            "--out",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode in (0, 1), proc.stderr + proc.stdout
    assert "run_id=" in proc.stdout

    rd = list(out.iterdir())[0]
    assert (rd / "run.json").is_file()
    assert (rd / "report.md").is_file()

    data = json.loads((rd / "run.json").read_text(encoding="utf-8"))
    assert data["meta"]["profile"] == "pm"
    assert "AAPL" in data["meta"]["symbols"]
    assert "plan" in data
    assert len(data["plan"]["steps"]) == 4
    report = (rd / "report.md").read_text(encoding="utf-8")
    assert "AAPL" in report
    assert "盘前研究简报" in report
