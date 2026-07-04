"""CLI 入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from briefpaws.config import DEFAULT_OUT_DIR, DEFAULT_PROFILE, DEFAULT_RANGE, MAX_SYMBOLS
from briefpaws.pipeline import run_brief
from briefpaws.storage.runs import save_run


def _parse_symbols(args: argparse.Namespace) -> list[str]:
    raw = args.symbols or args.symbol
    if not raw:
        raise SystemExit("需要 --symbols 或 --symbol")
    parts = [p.strip().upper() for p in raw.replace(" ", ",").split(",") if p.strip()]
    if not parts:
        raise SystemExit("标的列表为空")
    if len(parts) > MAX_SYMBOLS:
        raise SystemExit(f"最多 {MAX_SYMBOLS} 只标的，当前 {len(parts)}")
    return parts


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="briefpaws", description="BriefPaws L0b pre-market brief")
    p.add_argument("--symbols", help="逗号分隔，最多10只")
    p.add_argument("--symbol", help="单只（兼容）")
    p.add_argument("--range", default=DEFAULT_RANGE)
    p.add_argument("--profile", choices=["pm"], default=DEFAULT_PROFILE)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    symbols = _parse_symbols(args)
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    doc, report_md = run_brief(symbols, range_str=args.range, profile=args.profile)
    run_path = save_run(out_dir, doc, report_md)

    print(f"run_id={doc.meta.run_id}")
    print(f"status={doc.meta.status}")
    print(f"output={run_path}")
    return 0 if doc.meta.status != "failed" else 1


if __name__ == "__main__":
    sys.exit(main())
