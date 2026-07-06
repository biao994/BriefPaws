"""tool.get_latest_news — mock jsonl，按隔夜窗口过滤。"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from briefpaws.config import DATA_DIR, DEFAULT_TIMEZONE
from briefpaws.schemas.run import EvidenceLevel, NewsItem

_SOURCE_LEVEL: dict[str, EvidenceLevel] = {
    "sec": "filing",
    "edgar": "filing",
    "ir": "official",
    "prnewswire": "official",
    "finnhub": "aggregator",
}


def _overnight_bounds(now: datetime, tz_name: str) -> tuple[datetime, datetime]:
    tz = ZoneInfo(tz_name)
    now_local = now.astimezone(tz)
    end = now_local.replace(hour=9, minute=0, second=0, microsecond=0)
    if now_local.hour < 9:
        end = end - timedelta(days=1)
    start = (end - timedelta(days=1)).replace(hour=16, minute=0, second=0, microsecond=0)
    return start, end


def get_latest_news(
    symbol: str,
    *,
    mock_path: Path | None = None,
    tz_name: str = DEFAULT_TIMEZONE,
    now: datetime | None = None,
) -> list[NewsItem]:
    path = mock_path or (DATA_DIR / "news_mock.jsonl")
    if not path.exists():
        return []

    now = now or datetime.now(ZoneInfo("UTC"))
    start, end = _overnight_bounds(now, tz_name)
    items: list[NewsItem] = []

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("symbol", "").upper() != symbol.upper():
                continue
            t = datetime.fromisoformat(row["time"].replace("Z", "+00:00"))
            t_local = t.astimezone(ZoneInfo(tz_name))
            if not (start <= t_local <= end):
                continue
            src = row.get("source", "unknown").lower()
            items.append(
                NewsItem(
                    title=row["title"],
                    url=row["url"],
                    time=row["time"],
                    source=row.get("source", "unknown"),
                    evidence_level=_SOURCE_LEVEL.get(src, "unknown"),
                    summary=row.get("summary"),
                )
            )
    items.sort(key=lambda x: x.time, reverse=True)
    return items[:3]
