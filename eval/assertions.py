"""eval 数据集硬断言 — L0b 第 3 步。"""

from __future__ import annotations

import json
import re
from pathlib import Path

PM_EVIDENCE_PHRASE = "当前检索范围内未发现足够新闻"
REQUIRED_PM_PREMARKET_SECTIONS = ("总览", "行情与风险快照", "隔夜事件要点", "证据与不足")
REQUIRED_PM_MEMO_SECTIONS = ("核心观点", "催化剂", "异动与归因", "证据与局限")
REQUIRED_QUANT_SECTIONS = ("总览", "指标快照", "规则触发")


def load_run_artifacts(run_dir: Path) -> tuple[dict, str]:
    run_json = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    report_md = (run_dir / "report.md").read_text(encoding="utf-8")
    return run_json, report_md


def assert_artifacts_exist(run_dir: Path) -> list[str]:
    errors: list[str] = []
    if not (run_dir / "run.json").is_file():
        errors.append("missing run.json")
    if not (run_dir / "report.md").is_file():
        errors.append("missing report.md")
    return errors


def assert_required_sections(profile: str, report_md: str, run_json: dict | None = None) -> list[str]:
    if profile == "quant":
        sections = REQUIRED_QUANT_SECTIONS
    elif run_json and run_json.get("meta", {}).get("plan_variant") == "pm_memo":
        sections = REQUIRED_PM_MEMO_SECTIONS
    else:
        sections = REQUIRED_PM_PREMARKET_SECTIONS
    return [f"missing section: {s}" for s in sections if s not in report_md]


def assert_question_in_report(run_json: dict, report_md: str) -> list[str]:
    q = run_json.get("meta", {}).get("question")
    if q and q not in report_md:
        return ["question not reflected in report.md"]
    return []


def assert_plan_steps(run_json: dict) -> list[str]:
    errors: list[str] = []
    steps = (run_json.get("plan") or {}).get("steps") or []
    if len(steps) < 4:
        errors.append(f"plan.steps count {len(steps)} < 4")
    done = [s for s in steps if s.get("status") == "done"]
    if len(done) < 4:
        errors.append(f"plan.steps done {len(done)} < 4")
    return errors


def assert_numbers_traceable(run_json: dict, report_md: str) -> list[str]:
    errors: list[str] = []
    pct_pattern = re.compile(r"(-?\d+\.\d+)%")
    report_pcts = [float(x) / 100 for x in pct_pattern.findall(report_md)]
    if not report_pcts:
        return errors
    json_values: list[float] = []
    for sym in run_json.get("symbols") or []:
        ind = sym.get("indicators") or {}
        for key in ("return_3m", "vol_20d_ann", "mdd_3m", "overnight_gap", "worst_1d_return_20d"):
            val = ind.get(key)
            if val is not None:
                json_values.append(float(val))
    for rv in report_pcts:
        if not any(abs(rv - jv) < 0.0006 for jv in json_values):
            errors.append(f"untraceable pct in report: {rv:.2%}")
    return errors[:3]


def assert_pm_evidence_guard(run_json: dict, report_md: str) -> list[str]:
    errors: list[str] = []
    if run_json.get("meta", {}).get("profile") != "pm":
        return errors
    for sym in run_json.get("symbols") or []:
        if not (sym.get("news") or []) and "pm_attribution" in (sym.get("evidence_gaps") or []):
            if PM_EVIDENCE_PHRASE not in report_md:
                errors.append(f"{sym.get('symbol')}: pm evidence guard missing")
    return errors


def assert_hypothesis_reflection(run_json: dict, report_md: str) -> list[str]:
    errors: list[str] = []
    meta = run_json.get("meta") or {}
    if meta.get("profile") == "pm" and meta.get("question"):
        if not run_json.get("hypothesis"):
            errors.append("missing hypothesis for pm_memo with question")
        elif "假设验证" not in report_md:
            errors.append("hypothesis not in report.md")
    if run_json.get("reflection") is None:
        errors.append("missing reflection")
    return errors


def run_hard_assertions(run_dir: Path, profile: str) -> list[str]:
    errors = assert_artifacts_exist(run_dir)
    if errors:
        return errors
    run_json, report_md = load_run_artifacts(run_dir)
    errors.extend(assert_required_sections(profile, report_md, run_json))
    errors.extend(assert_question_in_report(run_json, report_md))
    errors.extend(assert_plan_steps(run_json))
    errors.extend(assert_numbers_traceable(run_json, report_md))
    errors.extend(assert_pm_evidence_guard(run_json, report_md))
    errors.extend(assert_hypothesis_reflection(run_json, report_md))
    return errors
