"""
تشخیص نواحی Supply (عرضه) و Demand (تقاضا).

روش: یافتن نواحی تثبیت قیمت (rally/drop-base-rally/drop) با چند کندل کوچک (base)
که سپس یک حرکت انفجاری از آن ناحیه خارج می‌شود.
"""
from typing import List
import pandas as pd
from ..core.data_models import Zone


def detect_supply_demand_zones(df: pd.DataFrame, base_max_candles: int = 4,
                                impulse_atr_mult: float = 1.8) -> List[Zone]:
    zones: List[Zone] = []
    if "atr" not in df.columns:
        raise ValueError("ستون 'atr' لازم است؛ ابتدا compute_all_indicators را اجرا کنید")

    n = len(df)
    i = 1
    while i < n - 1:
        atr_val = df["atr"].iloc[i]
        if pd.isna(atr_val) or atr_val == 0:
            i += 1
            continue

        body = abs(df["close"].iloc[i] - df["open"].iloc[i])
        candle_range = df["high"].iloc[i] - df["low"].iloc[i]

        # کندل "base" کوچک: بدنه کوچک نسبت به ATR
        if candle_range < 0.6 * atr_val:
            base_start = i
            base_end = i
            j = i + 1
            while j < n and (df["high"].iloc[j] - df["low"].iloc[j]) < 0.6 * atr_val and (j - base_start) < base_max_candles:
                base_end = j
                j += 1

            if j < n:
                impulse_body = abs(df["close"].iloc[j] - df["open"].iloc[j])
                if impulse_body > impulse_atr_mult * df["atr"].iloc[j]:
                    zone_top = df["high"].iloc[base_start:base_end + 1].max()
                    zone_bottom = df["low"].iloc[base_start:base_end + 1].min()
                    kind = "demand" if df["close"].iloc[j] > df["open"].iloc[j] else "supply"
                    zones.append(Zone(
                        kind=kind,
                        start_time=df["time"].iloc[base_start],
                        end_time=df["time"].iloc[base_end],
                        top=zone_top,
                        bottom=zone_bottom,
                        strength=impulse_body / df["atr"].iloc[j],
                    ))
            i = j
        else:
            i += 1

    return zones
