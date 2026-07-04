"""yfinance 不可用时生成合成日 K。"""

from __future__ import annotations

import numpy as np
import pandas as pd


def mock_price_frame(symbol: str, days: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(hash(symbol.upper()) % (2**32))
    dates = pd.bdate_range(end=pd.Timestamp.utcnow().normalize(), periods=days)
    ret = rng.normal(0.0005, 0.015, size=len(dates))
    close = 100.0 * np.cumprod(1 + ret)
    open_ = close * (1 + rng.normal(0, 0.002, len(dates)))
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.01, len(dates)))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.01, len(dates)))
    volume = rng.integers(5_000_000, 50_000_000, len(dates))
    return pd.DataFrame(
        {
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Adj Close": close,
            "Volume": volume,
        },
        index=dates,
    )
