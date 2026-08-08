"""اندیکاتورهای نوسان: Bollinger Bands (ATR در trend.py تعریف شده تا وابستگی SuperTrend حفظ شود)."""
import pandas as pd
from .trend import sma


def bollinger_bands(series: pd.Series, period: int = 20, std_mult: float = 2.0) -> pd.DataFrame:
    mid = sma(series, period)
    std = series.rolling(window=period).std()
    upper = mid + std_mult * std
    lower = mid - std_mult * std
    bandwidth = (upper - lower) / mid
    return pd.DataFrame({
        "bb_upper": upper,
        "bb_mid": mid,
        "bb_lower": lower,
        "bb_bandwidth": bandwidth,
    })
