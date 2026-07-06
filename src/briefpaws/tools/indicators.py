"""tool.compute_indicators — 六项固定指标。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from briefpaws.config import GAP_SIGMA_MULT, VOLUME_DRY_MULT, VOLUME_SPIKE_MULT
from briefpaws.schemas.run import Indicators, VolumeFlag


def compute_indicators(frame: pd.DataFrame) -> Indicators:
    if frame is None or len(frame) < 5:
        return Indicators()

    adj = frame["Adj Close"].astype(float)
    daily_ret = adj.pct_change().dropna()

    lookback = min(63, len(adj) - 1)
    ret_3m = float(adj.iloc[-1] / adj.iloc[-1 - lookback] - 1) if lookback > 0 else None

    vol_window = min(20, len(daily_ret))
    vol_20d = float(daily_ret.tail(vol_window).std() * np.sqrt(252)) if vol_window >= 2 else None

    window_3m = adj.tail(min(63, len(adj)))
    roll_max = window_3m.cummax()
    mdd_3m = float((window_3m / roll_max - 1.0).min()) if len(window_3m) else None

    open_t = float(frame["Open"].iloc[-1])
    close_prev = float(frame["Close"].iloc[-2]) if len(frame) >= 2 else float(frame["Close"].iloc[-1])
    gap = open_t / close_prev - 1.0 if close_prev else None
    gap_sig = False
    if gap is not None and vol_window >= 5:
        sigma = float(daily_ret.tail(vol_window).std())
        if sigma > 0 and abs(gap) > GAP_SIGMA_MULT * sigma:
            gap_sig = True

    vol_ratio = None
    vol_flag: VolumeFlag = "unknown"
    if "Volume" in frame.columns and len(frame) >= 21:
        vol = frame["Volume"].astype(float)
        mean20 = float(vol.tail(21).iloc[:-1].mean())
        today_v = float(vol.iloc[-1])
        if mean20 > 0:
            vol_ratio = today_v / mean20
            vol_flag = (
                "spike" if vol_ratio > VOLUME_SPIKE_MULT
                else "dry" if vol_ratio < VOLUME_DRY_MULT
                else "normal"
            )

    worst_1d = float(daily_ret.tail(min(20, len(daily_ret))).min()) if len(daily_ret) else None

    return Indicators(
        return_3m=ret_3m,
        vol_20d_ann=vol_20d,
        mdd_3m=mdd_3m,
        overnight_gap=gap,
        overnight_gap_significant=gap_sig,
        volume_ratio_20d=vol_ratio,
        volume_flag=vol_flag,
        worst_1d_return_20d=worst_1d,
    )
