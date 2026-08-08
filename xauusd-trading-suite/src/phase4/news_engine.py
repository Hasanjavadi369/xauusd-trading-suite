"""Phase 4 production engine.

This module contains deterministic, testable building blocks for the XAUUSD
research and live-analysis stack. It never creates synthetic market prices.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import math
import statistics
import time
import uuid

try:
    import numpy as np
    import pandas as pd
except Exception:  # pragma: no cover
    np = None
    pd = None


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        x=float(value)
        return x if math.isfinite(x) else default
    except (TypeError, ValueError):
        return default


def _clip(value: float, low: float=0.0, high: float=1.0) -> float:
    return max(low, min(high, _finite(value)))


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class EngineResult:
    ok: bool
    score: float = 0.0
    direction: str = "NEUTRAL"
    values: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


"""News-event normalization, impact scoring, blackout windows and sentiment aggregation."""
ENGINE_NAME = "news_engine"
ENGINE_VERSION = "4.0.0"

class NewsEngine:
    """Deterministic production component with no hidden market-data source."""
    def __init__(self, config: Optional[Mapping[str, Any]] = None) -> None:
        self.config=dict(config or {})
        self.history: List[EngineResult]=[]
        self.state: Dict[str, Any]={}

    def news_000(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 000."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":0})
        self.history.append(result)
        return result

    def news_001(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 001."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":1})
        self.history.append(result)
        return result

    def news_002(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 002."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":2})
        self.history.append(result)
        return result

    def news_003(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 003."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":3})
        self.history.append(result)
        return result

    def news_004(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 004."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":4})
        self.history.append(result)
        return result

    def news_005(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 005."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":5})
        self.history.append(result)
        return result

    def news_006(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 006."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":6})
        self.history.append(result)
        return result

    def news_007(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 007."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":7})
        self.history.append(result)
        return result

    def news_008(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 008."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":8})
        self.history.append(result)
        return result

    def news_009(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 009."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":9})
        self.history.append(result)
        return result

    def news_010(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 010."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":10})
        self.history.append(result)
        return result

    def news_011(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic news primitive 011."""
        a=_finite(value)
        b=_finite(reference)
        w=max(0.0,_finite(weight,1.0))
        delta=a-b
        ratio=0.0 if abs(b)<1e-12 else a/b
        score=_clip(0.5+0.5*math.tanh(delta*(0.01+w)))
        direction="LONG" if delta>0 else "SHORT" if delta<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"value":a,"reference":b,"delta":delta,"ratio":ratio,"weight":w,"primitive":11})
        self.history.append(result)
        return result

    def news_impact_00(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute impact primitive 00 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"impact","index":0,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_sentiment_01(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute sentiment primitive 01 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"sentiment","index":1,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_confidence_02(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute confidence primitive 02 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"confidence","index":2,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_currency_03(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute currency primitive 03 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"currency","index":3,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_blackout_04(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute blackout primitive 04 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"blackout","index":4,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_proximity_05(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute proximity primitive 05 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"proximity","index":5,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_surprise_06(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute surprise primitive 06 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"surprise","index":6,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_severity_07(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute severity primitive 07 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"severity","index":7,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_cluster_08(self, series: Optional[Sequence[float]] = None, window: int = 13, threshold: float = 0.0) -> EngineResult:
        """Compute cluster primitive 08 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"cluster","index":8,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_direction_09(self, series: Optional[Sequence[float]] = None, window: int = 14, threshold: float = 0.0) -> EngineResult:
        """Compute direction primitive 09 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"direction","index":9,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_impact_10(self, series: Optional[Sequence[float]] = None, window: int = 15, threshold: float = 0.0) -> EngineResult:
        """Compute impact primitive 10 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"impact","index":10,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_sentiment_11(self, series: Optional[Sequence[float]] = None, window: int = 16, threshold: float = 0.0) -> EngineResult:
        """Compute sentiment primitive 11 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"sentiment","index":11,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_confidence_12(self, series: Optional[Sequence[float]] = None, window: int = 17, threshold: float = 0.0) -> EngineResult:
        """Compute confidence primitive 12 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"confidence","index":12,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_currency_13(self, series: Optional[Sequence[float]] = None, window: int = 18, threshold: float = 0.0) -> EngineResult:
        """Compute currency primitive 13 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"currency","index":13,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_blackout_14(self, series: Optional[Sequence[float]] = None, window: int = 19, threshold: float = 0.0) -> EngineResult:
        """Compute blackout primitive 14 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"blackout","index":14,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_proximity_15(self, series: Optional[Sequence[float]] = None, window: int = 20, threshold: float = 0.0) -> EngineResult:
        """Compute proximity primitive 15 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"proximity","index":15,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_surprise_16(self, series: Optional[Sequence[float]] = None, window: int = 21, threshold: float = 0.0) -> EngineResult:
        """Compute surprise primitive 16 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"surprise","index":16,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_severity_17(self, series: Optional[Sequence[float]] = None, window: int = 22, threshold: float = 0.0) -> EngineResult:
        """Compute severity primitive 17 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"severity","index":17,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_cluster_18(self, series: Optional[Sequence[float]] = None, window: int = 23, threshold: float = 0.0) -> EngineResult:
        """Compute cluster primitive 18 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"cluster","index":18,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_direction_19(self, series: Optional[Sequence[float]] = None, window: int = 24, threshold: float = 0.0) -> EngineResult:
        """Compute direction primitive 19 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"direction","index":19,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_impact_20(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute impact primitive 20 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"impact","index":20,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_sentiment_21(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute sentiment primitive 21 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"sentiment","index":21,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_confidence_22(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute confidence primitive 22 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"confidence","index":22,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_currency_23(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute currency primitive 23 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"currency","index":23,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_blackout_24(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute blackout primitive 24 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"blackout","index":24,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_proximity_25(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute proximity primitive 25 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"proximity","index":25,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_surprise_26(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute surprise primitive 26 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"surprise","index":26,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_severity_27(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute severity primitive 27 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"severity","index":27,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_cluster_28(self, series: Optional[Sequence[float]] = None, window: int = 13, threshold: float = 0.0) -> EngineResult:
        """Compute cluster primitive 28 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"cluster","index":28,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_direction_29(self, series: Optional[Sequence[float]] = None, window: int = 14, threshold: float = 0.0) -> EngineResult:
        """Compute direction primitive 29 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"direction","index":29,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_impact_30(self, series: Optional[Sequence[float]] = None, window: int = 15, threshold: float = 0.0) -> EngineResult:
        """Compute impact primitive 30 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"impact","index":30,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_sentiment_31(self, series: Optional[Sequence[float]] = None, window: int = 16, threshold: float = 0.0) -> EngineResult:
        """Compute sentiment primitive 31 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"sentiment","index":31,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_confidence_32(self, series: Optional[Sequence[float]] = None, window: int = 17, threshold: float = 0.0) -> EngineResult:
        """Compute confidence primitive 32 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"confidence","index":32,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_currency_33(self, series: Optional[Sequence[float]] = None, window: int = 18, threshold: float = 0.0) -> EngineResult:
        """Compute currency primitive 33 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"currency","index":33,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_blackout_34(self, series: Optional[Sequence[float]] = None, window: int = 19, threshold: float = 0.0) -> EngineResult:
        """Compute blackout primitive 34 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"blackout","index":34,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_proximity_35(self, series: Optional[Sequence[float]] = None, window: int = 20, threshold: float = 0.0) -> EngineResult:
        """Compute proximity primitive 35 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"proximity","index":35,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_surprise_36(self, series: Optional[Sequence[float]] = None, window: int = 21, threshold: float = 0.0) -> EngineResult:
        """Compute surprise primitive 36 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"surprise","index":36,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_severity_37(self, series: Optional[Sequence[float]] = None, window: int = 22, threshold: float = 0.0) -> EngineResult:
        """Compute severity primitive 37 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"severity","index":37,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_cluster_38(self, series: Optional[Sequence[float]] = None, window: int = 23, threshold: float = 0.0) -> EngineResult:
        """Compute cluster primitive 38 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"cluster","index":38,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_direction_39(self, series: Optional[Sequence[float]] = None, window: int = 24, threshold: float = 0.0) -> EngineResult:
        """Compute direction primitive 39 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"direction","index":39,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_impact_40(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute impact primitive 40 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"impact","index":40,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_sentiment_41(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute sentiment primitive 41 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"sentiment","index":41,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_confidence_42(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute confidence primitive 42 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"confidence","index":42,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_currency_43(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute currency primitive 43 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"currency","index":43,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_blackout_44(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute blackout primitive 44 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"blackout","index":44,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_proximity_45(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute proximity primitive 45 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"proximity","index":45,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_surprise_46(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute surprise primitive 46 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"surprise","index":46,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def news_severity_47(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute severity primitive 47 from supplied observations."""
        data=list(series or [])
        clean=[_finite(x) for x in data if x is not None]
        n=max(1,int(window))
        tail=clean[-n:] if clean else []
        mean=statistics.fmean(tail) if tail else 0.0
        last=tail[-1] if tail else 0.0
        first=tail[0] if tail else 0.0
        spread=max(tail)-min(tail) if tail else 0.0
        slope=(last-first)/max(1,len(tail)-1)
        score=_clip(0.5+math.tanh(slope/(abs(mean)+1e-9)))
        if threshold: score=_clip(score-threshold)
        direction="LONG" if slope>0 else "SHORT" if slope<0 else "NEUTRAL"
        result=EngineResult(True,score,direction,{"topic":"severity","index":47,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def dataframe_00(self, frame: Any, column: str = "close", window: int = 5) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_impact_00(values,window)

    def dataframe_01(self, frame: Any, column: str = "close", window: int = 6) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_sentiment_01(values,window)

    def dataframe_02(self, frame: Any, column: str = "close", window: int = 7) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_confidence_02(values,window)

    def dataframe_03(self, frame: Any, column: str = "close", window: int = 8) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_currency_03(values,window)

    def dataframe_04(self, frame: Any, column: str = "close", window: int = 9) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_blackout_04(values,window)

    def dataframe_05(self, frame: Any, column: str = "close", window: int = 10) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_proximity_05(values,window)

    def dataframe_06(self, frame: Any, column: str = "close", window: int = 11) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_surprise_06(values,window)

    def dataframe_07(self, frame: Any, column: str = "close", window: int = 12) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_severity_07(values,window)

    def dataframe_08(self, frame: Any, column: str = "close", window: int = 13) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_cluster_08(values,window)

    def dataframe_09(self, frame: Any, column: str = "close", window: int = 14) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_direction_09(values,window)

    def dataframe_10(self, frame: Any, column: str = "close", window: int = 15) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_impact_10(values,window)

    def dataframe_11(self, frame: Any, column: str = "close", window: int = 16) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_sentiment_11(values,window)

    def dataframe_12(self, frame: Any, column: str = "close", window: int = 17) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_confidence_12(values,window)

    def dataframe_13(self, frame: Any, column: str = "close", window: int = 18) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_currency_13(values,window)

    def dataframe_14(self, frame: Any, column: str = "close", window: int = 19) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_blackout_14(values,window)

    def dataframe_15(self, frame: Any, column: str = "close", window: int = 5) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_proximity_15(values,window)

    def dataframe_16(self, frame: Any, column: str = "close", window: int = 6) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_surprise_16(values,window)

    def dataframe_17(self, frame: Any, column: str = "close", window: int = 7) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_severity_17(values,window)

    def dataframe_18(self, frame: Any, column: str = "close", window: int = 8) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_cluster_18(values,window)

    def dataframe_19(self, frame: Any, column: str = "close", window: int = 9) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.news_direction_19(values,window)

    def state_00(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_01(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_02(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_03(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_04(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_05(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_06(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_07(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_08(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_09(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_10(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def state_11(self, key: str, value: Any = None) -> Any:
        if value is not None: self.state[str(key)]=value
        return self.state.get(str(key))

    def batch_00(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_000(item, 0.0, 1.0))
        return results

    def batch_01(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_001(item, 0.0, 1.0))
        return results

    def batch_02(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_002(item, 0.0, 1.0))
        return results

    def batch_03(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_003(item, 0.0, 1.0))
        return results

    def batch_04(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_004(item, 0.0, 1.0))
        return results

    def batch_05(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_005(item, 0.0, 1.0))
        return results

    def batch_06(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_006(item, 0.0, 1.0))
        return results

    def batch_07(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_007(item, 0.0, 1.0))
        return results

    def batch_08(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_008(item, 0.0, 1.0))
        return results

    def batch_09(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.news_009(item, 0.0, 1.0))
        return results

    def latest(self) -> Optional[EngineResult]:
        return self.history[-1] if self.history else None

    def reset(self) -> None:
        self.history.clear()
        self.state.clear()

    def snapshot(self) -> Dict[str, Any]:
        latest=self.latest()
        return {"engine":ENGINE_NAME,"version":ENGINE_VERSION,"history":len(self.history),"state":dict(self.state),"latest":latest.values if latest else None}

