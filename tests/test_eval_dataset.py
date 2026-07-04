"""Eval 数据集回归 — 硬断言。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RUN_PY = ROOT / "run.py"
DATASET = ROOT / "eval" / "dataset.yaml"


def _load_cases() -> list[dict]:
    data = yaml.safe_load(DATASET.read_text(encoding="utf-8"))
    return data["cases"]


def _run_cli(case: dict, out: Path) -> Path:
    cmd = [
        sys.executable,
        str(RUN_PY),
        "--symbols",
        case["symbols"],
        "--profile",
        case["profile"],
        "--out",
        str(out),
    ]

    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "BRIEFPAWS_DATA": "mock"},
    )
    assert proc.returncode in (0, 1), proc.stderr + proc.stdout
    return list(out.iterdir())[0]


@pytest.mark.parametrize("case", _load_cases(), ids=lambda c: c["id"])
def test_dataset_case(case: dict, tmp_path: Path) -> None:
    from eval.assertions import run_hard_assertions

    run_dir = _run_cli(case, tmp_path / "runs")
    errors = run_hard_assertions(run_dir, case["profile"])
    assert not errors, errors


def test_plan_steps_in_run_json(tmp_path: Path) -> None:
    run_dir = _run_cli({"symbols": "AAPL", "profile": "pm"}, tmp_path / "runs")
    data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert len(data["plan"]["steps"]) == 4
    assert all(s["status"] == "done" for s in data["plan"]["steps"])


def test_graph_import() -> None:
    from briefpaws.graph import build_research_graph

    assert build_research_graph() is not None
