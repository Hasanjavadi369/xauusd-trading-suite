"""Market-regime detection using only information available at/ before each candle."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Regime:
    name: str
    score: float
    trend: str
    volatility: str
    reason: str

def detect_regime(df: pd.DataFrame, lookback: int = 50) -> Regime:
    if len(df) < max(20, lookback):
        return Regime("unknown", 0.0, "unknown", "unknown", "insufficient_history")
    x = df.tail(lookback).copy()
    close = pd.to_numeric(x["close"], errors="coerce")
    ret = close.pct_change().dropna()
    if len(ret) < 10:
        return Regime("unknown", 0.0, "unknown", "unknown", "insufficient_history")
    slope = np.polyfit(np.arange(len(close)), close.ffill().to_numpy(), 1)[0]
    scale = float(close.iloc[-1]) or 1.0
    trend_strength = abs(slope) * len(close) / scale
    vol = float(ret.std())
    med_vol = float(ret.abs().median()) or 1e-9
    volatility = "high" if vol > med_vol * 2.0 else ("low" if vol < med_vol * 0.75 else "normal")
    if trend_strength < 0.002:
        trend = "range"
    else:
        trend = "up" if slope > 0 else "down"
    score = min(1.0, trend_strength / 0.02)
    name = f"{trend}_{volatility}"
    return Regime(name, round(score, 4), trend, volatility, f"slope={slope:.6g},ret_std={vol:.6g}")
