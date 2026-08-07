"""
تشخیص الگوهای کندل‌استیک رایج: Pin Bar/Hammer, Engulfing, Doji, Morning/Evening Star.

خروجی هر تابع: pd.Series بولی هم‌طول دیتافریم که True یعنی الگو در آن کندل رخ داده.
"""
import pandas as pd


def _body(df):
    return (df["close"] - df["open"]).abs()


def _range(df):
    return df["high"] - df["low"]


def is_doji(df: pd.DataFrame, body_ratio: float = 0.1) -> pd.Series:
    rng = _range(df).replace(0, 1e-10)
    return (_body(df) / rng) < body_ratio


def is_bullish_pin_bar(df: pd.DataFrame, wick_ratio: float = 2.0) -> pd.Series:
    lower_wick = df[["open", "close"]].min(axis=1) - df["low"]
    upper_wick = df["high"] - df[["open", "close"]].max(axis=1)
    body = _body(df).replace(0, 1e-10)
    return (lower_wick > wick_ratio * body) & (lower_wick > 2 * upper_wick)


def is_bearish_pin_bar(df: pd.DataFrame, wick_ratio: float = 2.0) -> pd.Series:
    lower_wick = df[["open", "close"]].min(axis=1) - df["low"]
    upper_wick = df["high"] - df[["open", "close"]].max(axis=1)
    body = _body(df).replace(0, 1e-10)
    return (upper_wick > wick_ratio * body) & (upper_wick > 2 * lower_wick)


def is_bullish_engulfing(df: pd.DataFrame) -> pd.Series:
    prev_bearish = df["close"].shift(1) < df["open"].shift(1)
    curr_bullish = df["close"] > df["open"]
    engulf = (df["open"] <= df["close"].shift(1)) & (df["close"] >= df["open"].shift(1))
    return prev_bearish & curr_bullish & engulf


def is_bearish_engulfing(df: pd.DataFrame) -> pd.Series:
    prev_bullish = df["close"].shift(1) > df["open"].shift(1)
    curr_bearish = df["close"] < df["open"]
    engulf = (df["open"] >= df["close"].shift(1)) & (df["close"] <= df["open"].shift(1))
    return prev_bullish & curr_bearish & engulf


def is_morning_star(df: pd.DataFrame) -> pd.Series:
    c1_bearish = df["close"].shift(2) < df["open"].shift(2)
    c2_small = _body(df).shift(1) < 0.3 * _body(df).shift(2)
    c3_bullish = (df["close"] > df["open"]) & (df["close"] > (df["open"].shift(2) + df["close"].shift(2)) / 2)
    return c1_bearish & c2_small & c3_bullish


def is_evening_star(df: pd.DataFrame) -> pd.Series:
    c1_bullish = df["close"].shift(2) > df["open"].shift(2)
    c2_small = _body(df).shift(1) < 0.3 * _body(df).shift(2)
    c3_bearish = (df["close"] < df["open"]) & (df["close"] < (df["open"].shift(2) + df["close"].shift(2)) / 2)
    return c1_bullish & c2_small & c3_bearish


def detect_all_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """همه‌ی الگوها را به‌صورت ستون‌های بولی به دیتافریم اضافه می‌کند."""
    out = df.copy()
    out["pattern_doji"] = is_doji(df)
    out["pattern_bullish_pin"] = is_bullish_pin_bar(df)
    out["pattern_bearish_pin"] = is_bearish_pin_bar(df)
    out["pattern_bullish_engulfing"] = is_bullish_engulfing(df)
    out["pattern_bearish_engulfing"] = is_bearish_engulfing(df)
    out["pattern_morning_star"] = is_morning_star(df)
    out["pattern_evening_star"] = is_evening_star(df)
    return out
