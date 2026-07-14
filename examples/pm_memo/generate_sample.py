"""在 examples/pm_memo/sample/ 下生成固定 PM 演示产物。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = Path(__file__).resolve().parent / "sample"


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from briefpaws.pipeline import run_brief
    from briefpaws.storage.runs import save_run

    question = "隔夜是否有影响开盘的披露？"
    doc, report_md = run_brief(
        ["AAPL", "MSFT", "NVDA"],
        profile="pm",
        question=question,
    )

    if SAMPLE_DIR.exists():
        shutil.rmtree(SAMPLE_DIR)
    SAMPLE_DIR.mkdir(parents=True)
    save_run(SAMPLE_DIR, doc, report_md)

    print(f"sample_run_id={doc.meta.run_id}")
    print(f"output={SAMPLE_DIR / doc.meta.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
