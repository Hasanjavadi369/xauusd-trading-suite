"""محاسبه یکجای همه اندیکاتورها روی دیتافریم OHLC بر اساس تنظیمات config."""
import pandas as pd
from . import trend, momentum, volatility, volume


def compute_all_indicators(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    df باید شامل ستون‌های time, open, high, low, close, volume باشد.
    خروجی: همان دیتافریم به همراه ستون‌های اندیکاتورهای محاسبه‌شده.
    """
    out = df.copy()
    ind_cfg = config.get("indicators", {})

    for period in ind_cfg.get("ema_periods", [20, 50, 200]):
        out[f"ema_{period}"] = trend.ema(out["close"], period)

    for period in ind_cfg.get("sma_periods", [50, 200]):
        out[f"sma_{period}"] = trend.sma(out["close"], period)

    out["rsi"] = momentum.rsi(out["close"], ind_cfg.get("rsi_period", 14))

    macd_cfg = ind_cfg.get("macd", {"fast": 12, "slow": 26, "signal": 9})
    macd_df = momentum.macd(out["close"], macd_cfg["fast"], macd_cfg["slow"], macd_cfg["signal"])
    out = pd.concat([out, macd_df], axis=1)

    out["atr"] = trend.atr(out, ind_cfg.get("atr_period", 14))
    out["adx"] = trend.adx(out, ind_cfg.get("adx_period", 14))

    bb_cfg = ind_cfg.get("bollinger", {"period": 20, "std": 2})
    bb_df = volatility.bollinger_bands(out["close"], bb_cfg["period"], bb_cfg["std"])
    out = pd.concat([out, bb_df], axis=1)

    st_cfg = ind_cfg.get("supertrend", {"period": 10, "multiplier": 3})
    st_df = trend.supertrend(out, st_cfg["period"], st_cfg["multiplier"])
    out = pd.concat([out, st_df], axis=1)

    ichi_cfg = ind_cfg.get("ichimoku", {"tenkan": 9, "kijun": 26, "senkou_b": 52})
    ichi_df = trend.ichimoku(out, ichi_cfg["tenkan"], ichi_cfg["kijun"], ichi_cfg["senkou_b"])
    out = pd.concat([out, ichi_df], axis=1)

    if "time" in out.columns:
        out["vwap"] = volume.vwap(out)

    return out
