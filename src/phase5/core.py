"""Phase 5: production-grade quantitative core.

No synthetic market data is generated here. Every decision is derived from
caller supplied OHLCV observations and explicit execution constraints.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Sequence, Mapping, Any
import math
import statistics

@dataclass(frozen=True)
class Candle:
    timestamp: Any
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

@dataclass(frozen=True)
class MarketSnapshot:
    price: float
    atr: float
    trend: float
    momentum: float
    volatility: float
    range_high: float
    range_low: float
    confidence: float

@dataclass(frozen=True)
class TradePlan:
    side: str
    entry: float
    stop_loss: float
    take_profit: float
    risk_distance: float
    reward_distance: float
    rr: float
    confidence: float
    valid: bool
    reason: str = ""

@dataclass(frozen=True)
class BrokerRules:
    digits: int = 2
    point: float = 0.01
    min_stop_points: float = 0.0
    spread_points: float = 0.0
    max_spread_points: float = 100.0

def _finite(x: Any) -> float:
    try:
        y=float(x)
        return y if math.isfinite(y) else math.nan
    except (TypeError, ValueError):
        return math.nan

def clean_candles(rows: Sequence[Mapping[str, Any]], require_volume: bool=False) -> list[Candle]:
    out=[]
    for r in rows:
        try:
            o,h,l,c=map(_finite,(r["open"],r["high"],r["low"],r["close"]))
            v=_finite(r.get("volume",0.0))
            if any(math.isnan(x) for x in (o,h,l,c)) or h<max(o,c) or l>min(o,c) or l>h:
                continue
            if require_volume and (math.isnan(v) or v<0):
                continue
            out.append(Candle(r.get("timestamp"),o,h,l,c,0.0 if math.isnan(v) else v))
        except (KeyError,TypeError):
            continue
    return out

def atr(candles: Sequence[Candle], period: int=14) -> float:
    if len(candles)<2: return 0.0
    trs=[]
    for prev,cur in zip(candles[:-1],candles[1:]):
        trs.append(max(cur.high-cur.low,abs(cur.high-prev.close),abs(cur.low-prev.close)))
    p=max(1,int(period)); tail=trs[-p:]
    return statistics.fmean(tail) if tail else 0.0

def slope(values: Sequence[float], window: int=20) -> float:
    x=list(map(float,values[-max(2,int(window)):]))
    if len(x)<2:return 0.0
    n=len(x); mx=(n-1)/2; my=statistics.fmean(x)
    den=sum((i-mx)**2 for i in range(n))
    return sum((i-mx)*(y-my) for i,y in enumerate(x))/den if den else 0.0

def momentum(values: Sequence[float], lookback: int=10) -> float:
    x=list(map(float,values)); n=max(1,int(lookback))
    if len(x)<=n or x[-n-1]==0:return 0.0
    return x[-1]/x[-n-1]-1.0

def snapshot(candles: Sequence[Candle], trend_window: int=30, atr_period: int=14) -> MarketSnapshot:
    if not candles: raise ValueError("at least one candle is required")
    closes=[c.close for c in candles]; a=atr(candles,atr_period); p=closes[-1]
    tr=slope(closes,trend_window); mom=momentum(closes, min(10,len(closes)-1))
    vol=(a/p) if p else 0.0
    hi=max(c.high for c in candles[-trend_window:]); lo=min(c.low for c in candles[-trend_window:])
    raw=min(1.0,abs(tr)/(a+1e-12)) if a else 0.0
    conf=max(0.0,min(1.0,0.5*raw+0.5*min(1.0,abs(mom)*100)))
    return MarketSnapshot(p,a,tr,mom,vol,hi,lo,conf)

def round_price(price: float, digits: int) -> float:
    return round(float(price), max(0,int(digits)))

def build_trade_plan(s: MarketSnapshot, side: str, rules: BrokerRules, rr_target: float=2.0,
                     atr_mult: float=1.5, buffer_points: float=2.0) -> TradePlan:
    side=side.upper(); p=s.price
    if side not in {"BUY","SELL"}: return TradePlan(side,p,p,p,0,0,0,s.confidence,False,"invalid side")
    if rules.spread_points>rules.max_spread_points:
        return TradePlan(side,p,p,p,0,0,0,s.confidence,False,"spread exceeds limit")
    min_dist=max(rules.min_stop_points*rules.point, buffer_points*rules.point)
    structure=(p-s.range_low) if side=="BUY" else (s.range_high-p)
    distance=max(min_dist, atr_mult*s.atr, structure+min_dist if structure>0 else 0.0)
    sl=p-distance if side=="BUY" else p+distance
    tp=p+distance*max(1.0,float(rr_target)) if side=="BUY" else p-distance*max(1.0,float(rr_target))
    sl,tp=round_price(sl,rules.digits),round_price(tp,rules.digits)
    risk=abs(p-sl); reward=abs(tp-p); rr=reward/risk if risk else 0.0
    valid=(sl<p<tp if side=="BUY" else tp<p<sl) and rr>=max(1.0,float(rr_target))
    return TradePlan(side,round_price(p,rules.digits),sl,tp,risk,reward,rr,s.confidence,valid,"" if valid else "invalid geometry")

def feature_vector(candles: Sequence[Candle]) -> dict[str,float]:
    s=snapshot(candles)
    return {"close":s.price,"atr":s.atr,"trend":s.trend,"momentum":s.momentum,
            "volatility":s.volatility,"range_high":s.range_high,"range_low":s.range_low,
            "confidence":s.confidence}
