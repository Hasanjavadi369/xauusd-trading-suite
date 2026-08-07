"""Leakage-safe multi-timeframe trend/confluence helpers."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from .regime import detect_regime

@dataclass(frozen=True)
class TimeframeView:
    timeframe: str
    trend: str
    regime: str
    score: float

def analyze_timeframes(frames: dict[str, pd.DataFrame]) -> list[TimeframeView]:
    out=[]
    for tf, df in frames.items():
        r=detect_regime(df)
        out.append(TimeframeView(tf,r.trend,r.name,r.score))
    return out

def confluence_score(frames: dict[str, pd.DataFrame], direction: str) -> float:
    views=analyze_timeframes(frames)
    if not views: return 0.0
    weights={"M1":0.5,"M5":0.7,"M15":0.9,"M30":1.0,"H1":1.2,"H4":1.4,"D1":1.6}
    total=weight_sum=0.0
    for v in views:
        w=weights.get(v.timeframe,1.0); weight_sum+=w
        if v.trend == direction: total += w*(0.5+0.5*v.score)
        elif v.trend == "range": total += 0.15*w
    return round(total/weight_sum,4) if weight_sum else 0.0
