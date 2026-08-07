"""
تشخیص Fair Value Gap (FVG) — شکاف بین کندل ۱ و کندل ۳ که کندل ۲ آن را پر نمی‌کند.

Bullish FVG: low(candle 3) > high(candle 1)
Bearish FVG: high(candle 3) < low(candle 1)
"""
from typing import List
import pandas as pd
from ..core.data_models import Zone


def detect_fvg(df: pd.DataFrame, min_gap_pct: float = 0.02) -> List[Zone]:
    zones: List[Zone] = []
    n = len(df)

    for i in range(2, n):
        c1_high, c1_low = df["high"].iloc[i - 2], df["low"].iloc[i - 2]
        c3_high, c3_low = df["high"].iloc[i], df["low"].iloc[i]
        mid_price = df["close"].iloc[i - 1]

        # Bullish FVG
        if c3_low > c1_high:
            gap_pct = (c3_low - c1_high) / mid_price * 100
            if gap_pct >= min_gap_pct:
                zones.append(Zone(
                    kind="fvg_bullish",
                    start_time=df["time"].iloc[i - 2],
                    end_time=df["time"].iloc[i],
                    top=c3_low,
                    bottom=c1_high,
                    strength=gap_pct,
                ))

        # Bearish FVG
        if c3_high < c1_low:
            gap_pct = (c1_low - c3_high) / mid_price * 100
            if gap_pct >= min_gap_pct:
                zones.append(Zone(
                    kind="fvg_bearish",
                    start_time=df["time"].iloc[i - 2],
                    end_time=df["time"].iloc[i],
                    top=c1_low,
                    bottom=c3_high,
                    strength=gap_pct,
                ))

    return zones


def mark_filled_fvgs(zones: List[Zone], df: pd.DataFrame) -> None:
    """اگر قیمت بعداً کل شکاف FVG را پر کند، mitigated=True می‌شود (in-place)."""
    for zone in zones:
        end_idx = df[df["time"] == zone.end_time].index
        if len(end_idx) == 0:
            continue
        start_search = end_idx[0] + 1
        for i in range(start_search, len(df)):
            if df["low"].iloc[i] <= zone.bottom and df["high"].iloc[i] >= zone.top:
                zone.mitigated = True
                break
