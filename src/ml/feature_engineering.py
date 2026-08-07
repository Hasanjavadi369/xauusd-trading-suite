"""
مهندسی ویژگی (Feature Engineering) برای مدل یادگیری ماشین.

ورودی: دیتافریمی که از قبل با `compute_all_indicators` و
`candlestick_patterns.detect_all_patterns` غنی‌شده است.
خروجی: ماتریس ویژگی عددی (بدون NaN) که مدل روی آن آموزش می‌بیند یا پیش‌بینی می‌کند.

طراحی به‌گونه‌ای است که هیچ ویژگی از داده‌ی آینده استفاده نکند (بدون Look-ahead Bias):
همه‌ی ویژگی‌ها فقط از کندل جاری و گذشته محاسبه می‌شوند.
"""
from typing import List
import numpy as np
import pandas as pd

FEATURE_COLUMNS: List[str] = [
    "return_1", "return_3", "return_5", "return_10",
    "rsi", "macd_hist_norm",
    "atr_norm", "adx",
    "bb_bandwidth", "bb_position",
    "ema_fast_slow_spread", "price_vs_ema200",
    "supertrend_direction",
    "body_ratio", "upper_wick_ratio", "lower_wick_ratio",
    "pattern_bullish_pin", "pattern_bearish_pin",
    "pattern_bullish_engulfing", "pattern_bearish_engulfing",
    "pattern_doji",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    df باید شامل خروجی compute_all_indicators و detect_all_patterns باشد.
    ستون‌های لازم حداقلی: close, high, low, open, rsi, macd_hist, atr, adx,
    bb_upper, bb_mid, bb_lower, ema_20/50/200 (یا مشابه), supertrend_direction.
    """
    out = pd.DataFrame(index=df.index)
    close = df["close"]

    out["return_1"] = close.pct_change(1)
    out["return_3"] = close.pct_change(3)
    out["return_5"] = close.pct_change(5)
    out["return_10"] = close.pct_change(10)

    out["rsi"] = df.get("rsi", pd.Series(50, index=df.index)) / 100.0

    macd_hist = df.get("macd_hist", pd.Series(0, index=df.index))
    out["macd_hist_norm"] = macd_hist / close

    atr = df.get("atr", pd.Series(np.nan, index=df.index))
    out["atr_norm"] = atr / close
    out["adx"] = df.get("adx", pd.Series(20, index=df.index)) / 100.0

    bb_upper = df.get("bb_upper")
    bb_lower = df.get("bb_lower")
    bb_mid = df.get("bb_mid")
    if bb_upper is not None and bb_lower is not None and bb_mid is not None:
        out["bb_bandwidth"] = (bb_upper - bb_lower) / bb_mid
        band_range = (bb_upper - bb_lower).replace(0, np.nan)
        out["bb_position"] = (close - bb_lower) / band_range
    else:
        out["bb_bandwidth"] = 0.0
        out["bb_position"] = 0.5

    ema_fast = df.get("ema_20")
    ema_slow = df.get("ema_50")
    ema_200 = df.get("ema_200")
    if ema_fast is not None and ema_slow is not None:
        out["ema_fast_slow_spread"] = (ema_fast - ema_slow) / close
    else:
        out["ema_fast_slow_spread"] = 0.0
    out["price_vs_ema200"] = (close - ema_200) / close if ema_200 is not None else 0.0

    out["supertrend_direction"] = df.get("supertrend_direction", pd.Series(0, index=df.index))

    body = (df["close"] - df["open"])
    candle_range = (df["high"] - df["low"]).replace(0, np.nan)
    out["body_ratio"] = body / candle_range
    out["upper_wick_ratio"] = (df["high"] - df[["open", "close"]].max(axis=1)) / candle_range
    out["lower_wick_ratio"] = (df[["open", "close"]].min(axis=1) - df["low"]) / candle_range

    for pattern_col in ["pattern_bullish_pin", "pattern_bearish_pin",
                        "pattern_bullish_engulfing", "pattern_bearish_engulfing",
                        "pattern_doji"]:
        out[pattern_col] = df.get(pattern_col, False).astype(float)

    out = out[FEATURE_COLUMNS]
    return out


def clean_features_labels(features: pd.DataFrame, labels: pd.Series):
    """حذف ردیف‌هایی که ویژگی یا برچسب NaN دارند (ابتدای سری به دلیل rolling/pct_change)."""
    combined = features.copy()
    combined["__label__"] = labels
    combined = combined.replace([np.inf, -np.inf], np.nan).dropna()
    y = combined.pop("__label__")
    return combined, y
