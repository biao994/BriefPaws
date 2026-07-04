"""tool.get_price_series — yfinance，失败时 mock 回退。"""

from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from briefpaws.config import DEFAULT_RANGE


@dataclass
class PriceSeriesResult:
    ok: bool
    error_code: str | None
    frame: pd.DataFrame | None


def _period_for_range(range_str: str) -> str:
    r = range_str.upper().strip()
    return "6mo" if r in ("3M", "90D", "3MO") else "6mo"


def get_price_series(symbol: str, range_str: str = DEFAULT_RANGE) -> PriceSeriesResult:
    # BRIEFPAWS_DATA=mock 时跳过 yfinance，离线/CI 用 mock 行情
    if os.environ.get("BRIEFPAWS_DATA", "").lower() != "mock":
        try:
            hist = yf.Ticker(symbol).history(
                period=_period_for_range(range_str), interval="1d", auto_adjust=False
            )
            if hist is not None and not hist.empty:
                hist = hist.rename(columns=str.title)
                if "Adj Close" not in hist.columns and "Close" in hist.columns:
                    hist["Adj Close"] = hist["Close"]
                return PriceSeriesResult(ok=True, error_code=None, frame=hist)
        except Exception:
            pass

    from briefpaws.tools.price_mock import mock_price_frame

    if symbol.upper().isalpha() and 1 <= len(symbol) <= 6:
        return PriceSeriesResult(ok=True, error_code=None, frame=mock_price_frame(symbol))
    return PriceSeriesResult(ok=False, error_code="INVALID_SYMBOL", frame=None)
