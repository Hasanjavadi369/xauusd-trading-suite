"""
تشخیص Order Blocks (OB) بر اساس مفهوم SMC:

Bullish OB: آخرین کندل نزولی قبل از یک حرکت صعودی قوی (که معمولاً یک سوینگ‌لو را
    می‌شکند و باعث BOS صعودی می‌شود).
Bearish OB: آخرین کندل صعودی قبل از یک حرکت نزولی قوی که سوینگ‌های قبلی را می‌شکند.
"""
from typing import List
import pandas as pd
from ..core.data_models import Zone


def detect_order_blocks(df: pd.DataFrame, lookback: int = 20, impulse_atr_mult: float = 1.5) -> List[Zone]:
    zones: List[Zone] = []
    if "atr" not in df.columns:
        raise ValueError("دیتافریم باید ستون 'atr' داشته باشد (از calculator.compute_all_indicators استفاده کنید)")

    n = len(df)
    for i in range(2, n):
        impulse_body = abs(df["close"].iloc[i] - df["open"].iloc[i])
        atr_val = df["atr"].iloc[i] if not pd.isna(df["atr"].iloc[i]) else 0
        if atr_val == 0:
            continue

        is_strong_impulse = impulse_body > impulse_atr_mult * atr_val

        # حرکت صعودی قوی -> جستجوی آخرین کندل نزولی قبل از آن به عنوان Bullish OB
        if is_strong_impulse and df["close"].iloc[i] > df["open"].iloc[i]:
            for j in range(i - 1, max(i - lookback, -1), -1):
                if df["close"].iloc[j] < df["open"].iloc[j]:
                    zones.append(Zone(
                        kind="order_block_bullish",
                        start_time=df["time"].iloc[j],
                        end_time=df["time"].iloc[i],
                        top=df["high"].iloc[j],
                        bottom=df["low"].iloc[j],
                        strength=impulse_body / atr_val,
                        metadata={"impulse_index": i, "ob_index": j},
                    ))
                    break

        # حرکت نزولی قوی -> جستجوی آخرین کندل صعودی قبل از آن به عنوان Bearish OB
        if is_strong_impulse and df["close"].iloc[i] < df["open"].iloc[i]:
            for j in range(i - 1, max(i - lookback, -1), -1):
                if df["close"].iloc[j] > df["open"].iloc[j]:
                    zones.append(Zone(
                        kind="order_block_bearish",
                        start_time=df["time"].iloc[j],
                        end_time=df["time"].iloc[i],
                        top=df["high"].iloc[j],
                        bottom=df["low"].iloc[j],
                        strength=impulse_body / atr_val,
                        metadata={"impulse_index": i, "ob_index": j},
                    ))
                    break

    return zones


def mark_mitigated_zones(zones: List[Zone], df: pd.DataFrame) -> None:
    """اگر قیمت بعداً وارد ناحیه OB شود، آن را mitigated=True علامت بزن (in-place)."""
    for zone in zones:
        end_idx = df[df["time"] == zone.end_time].index
        if len(end_idx) == 0:
            continue
        start_search = end_idx[0] + 1
        for i in range(start_search, len(df)):
            if df["low"].iloc[i] <= zone.top and df["high"].iloc[i] >= zone.bottom:
                zone.mitigated = True
                break
