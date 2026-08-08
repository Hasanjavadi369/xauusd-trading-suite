"""اندیکاتور حجمی: VWAP (Volume Weighted Average Price)."""
import pandas as pd


def vwap(df: pd.DataFrame, session_reset: bool = True) -> pd.Series:
    """
    VWAP تجمعی. اگر session_reset=True باشد، هر روز از نو محاسبه می‌شود
    (مناسب فارکس/طلا که سشن معاملاتی مشخص دارد).
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    tp_vol = typical_price * df["volume"]

    if session_reset:
        day = df["time"].dt.date
        cum_tp_vol = tp_vol.groupby(day).cumsum()
        cum_vol = df["volume"].groupby(day).cumsum()
    else:
        cum_tp_vol = tp_vol.cumsum()
        cum_vol = df["volume"].cumsum()

    return cum_tp_vol / cum_vol.replace(0, 1e-10)
