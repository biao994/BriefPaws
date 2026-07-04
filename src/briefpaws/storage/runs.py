"""落盘 run.json 与 report.md。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from briefpaws.schemas.run import RunDocument


def new_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


def save_run(out_root: Path, doc: RunDocument, report_md: str) -> Path:
    rd = out_root / doc.meta.run_id
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "run.json").write_text(doc.model_dump_json(indent=2), encoding="utf-8")
    (rd / "report.md").write_text(report_md, encoding="utf-8")
    return rd
