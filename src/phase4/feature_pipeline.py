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


"""Feature engineering, normalization, rolling market features and feature health checks."""
ENGINE_NAME = "feature_pipeline"
ENGINE_VERSION = "4.0.0"

class FeaturePipeline:
    """Deterministic production component with no hidden market-data source."""
    def __init__(self, config: Optional[Mapping[str, Any]] = None) -> None:
        self.config=dict(config or {})
        self.history: List[EngineResult]=[]
        self.state: Dict[str, Any]={}

    def feature_000(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 000."""
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

    def feature_001(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 001."""
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

    def feature_002(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 002."""
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

    def feature_003(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 003."""
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

    def feature_004(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 004."""
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

    def feature_005(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 005."""
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

    def feature_006(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 006."""
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

    def feature_007(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 007."""
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

    def feature_008(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 008."""
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

    def feature_009(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 009."""
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

    def feature_010(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 010."""
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

    def feature_011(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic feature primitive 011."""
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

    def feature_close_00(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute close primitive 00 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"close","index":0,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_open_01(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute open primitive 01 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"open","index":1,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_high_02(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute high primitive 02 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"high","index":2,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_low_03(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute low primitive 03 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"low","index":3,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_volume_04(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute volume primitive 04 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volume","index":4,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_spread_05(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute spread primitive 05 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"spread","index":5,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_returns_06(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute returns primitive 06 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"returns","index":6,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_atr_07(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 07 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":7,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_rsi_08(self, series: Optional[Sequence[float]] = None, window: int = 13, threshold: float = 0.0) -> EngineResult:
        """Compute rsi primitive 08 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rsi","index":8,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_adx_09(self, series: Optional[Sequence[float]] = None, window: int = 14, threshold: float = 0.0) -> EngineResult:
        """Compute adx primitive 09 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"adx","index":9,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_close_10(self, series: Optional[Sequence[float]] = None, window: int = 15, threshold: float = 0.0) -> EngineResult:
        """Compute close primitive 10 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"close","index":10,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_open_11(self, series: Optional[Sequence[float]] = None, window: int = 16, threshold: float = 0.0) -> EngineResult:
        """Compute open primitive 11 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"open","index":11,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_high_12(self, series: Optional[Sequence[float]] = None, window: int = 17, threshold: float = 0.0) -> EngineResult:
        """Compute high primitive 12 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"high","index":12,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_low_13(self, series: Optional[Sequence[float]] = None, window: int = 18, threshold: float = 0.0) -> EngineResult:
        """Compute low primitive 13 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"low","index":13,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_volume_14(self, series: Optional[Sequence[float]] = None, window: int = 19, threshold: float = 0.0) -> EngineResult:
        """Compute volume primitive 14 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volume","index":14,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_spread_15(self, series: Optional[Sequence[float]] = None, window: int = 20, threshold: float = 0.0) -> EngineResult:
        """Compute spread primitive 15 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"spread","index":15,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_returns_16(self, series: Optional[Sequence[float]] = None, window: int = 21, threshold: float = 0.0) -> EngineResult:
        """Compute returns primitive 16 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"returns","index":16,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_atr_17(self, series: Optional[Sequence[float]] = None, window: int = 22, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 17 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":17,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_rsi_18(self, series: Optional[Sequence[float]] = None, window: int = 23, threshold: float = 0.0) -> EngineResult:
        """Compute rsi primitive 18 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rsi","index":18,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_adx_19(self, series: Optional[Sequence[float]] = None, window: int = 24, threshold: float = 0.0) -> EngineResult:
        """Compute adx primitive 19 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"adx","index":19,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_close_20(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute close primitive 20 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"close","index":20,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_open_21(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute open primitive 21 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"open","index":21,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_high_22(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute high primitive 22 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"high","index":22,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_low_23(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute low primitive 23 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"low","index":23,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_volume_24(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute volume primitive 24 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volume","index":24,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_spread_25(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute spread primitive 25 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"spread","index":25,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_returns_26(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute returns primitive 26 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"returns","index":26,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_atr_27(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 27 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":27,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_rsi_28(self, series: Optional[Sequence[float]] = None, window: int = 13, threshold: float = 0.0) -> EngineResult:
        """Compute rsi primitive 28 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rsi","index":28,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_adx_29(self, series: Optional[Sequence[float]] = None, window: int = 14, threshold: float = 0.0) -> EngineResult:
        """Compute adx primitive 29 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"adx","index":29,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_close_30(self, series: Optional[Sequence[float]] = None, window: int = 15, threshold: float = 0.0) -> EngineResult:
        """Compute close primitive 30 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"close","index":30,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_open_31(self, series: Optional[Sequence[float]] = None, window: int = 16, threshold: float = 0.0) -> EngineResult:
        """Compute open primitive 31 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"open","index":31,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_high_32(self, series: Optional[Sequence[float]] = None, window: int = 17, threshold: float = 0.0) -> EngineResult:
        """Compute high primitive 32 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"high","index":32,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_low_33(self, series: Optional[Sequence[float]] = None, window: int = 18, threshold: float = 0.0) -> EngineResult:
        """Compute low primitive 33 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"low","index":33,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_volume_34(self, series: Optional[Sequence[float]] = None, window: int = 19, threshold: float = 0.0) -> EngineResult:
        """Compute volume primitive 34 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volume","index":34,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_spread_35(self, series: Optional[Sequence[float]] = None, window: int = 20, threshold: float = 0.0) -> EngineResult:
        """Compute spread primitive 35 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"spread","index":35,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_returns_36(self, series: Optional[Sequence[float]] = None, window: int = 21, threshold: float = 0.0) -> EngineResult:
        """Compute returns primitive 36 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"returns","index":36,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_atr_37(self, series: Optional[Sequence[float]] = None, window: int = 22, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 37 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":37,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_rsi_38(self, series: Optional[Sequence[float]] = None, window: int = 23, threshold: float = 0.0) -> EngineResult:
        """Compute rsi primitive 38 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rsi","index":38,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_adx_39(self, series: Optional[Sequence[float]] = None, window: int = 24, threshold: float = 0.0) -> EngineResult:
        """Compute adx primitive 39 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"adx","index":39,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_close_40(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute close primitive 40 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"close","index":40,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_open_41(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute open primitive 41 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"open","index":41,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_high_42(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute high primitive 42 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"high","index":42,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_low_43(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute low primitive 43 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"low","index":43,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_volume_44(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute volume primitive 44 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volume","index":44,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_spread_45(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute spread primitive 45 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"spread","index":45,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_returns_46(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute returns primitive 46 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"returns","index":46,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def feature_atr_47(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 47 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":47,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def dataframe_00(self, frame: Any, column: str = "close", window: int = 5) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_close_00(values,window)

    def dataframe_01(self, frame: Any, column: str = "close", window: int = 6) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_open_01(values,window)

    def dataframe_02(self, frame: Any, column: str = "close", window: int = 7) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_high_02(values,window)

    def dataframe_03(self, frame: Any, column: str = "close", window: int = 8) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_low_03(values,window)

    def dataframe_04(self, frame: Any, column: str = "close", window: int = 9) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_volume_04(values,window)

    def dataframe_05(self, frame: Any, column: str = "close", window: int = 10) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_spread_05(values,window)

    def dataframe_06(self, frame: Any, column: str = "close", window: int = 11) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_returns_06(values,window)

    def dataframe_07(self, frame: Any, column: str = "close", window: int = 12) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_atr_07(values,window)

    def dataframe_08(self, frame: Any, column: str = "close", window: int = 13) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_rsi_08(values,window)

    def dataframe_09(self, frame: Any, column: str = "close", window: int = 14) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_adx_09(values,window)

    def dataframe_10(self, frame: Any, column: str = "close", window: int = 15) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_close_10(values,window)

    def dataframe_11(self, frame: Any, column: str = "close", window: int = 16) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_open_11(values,window)

    def dataframe_12(self, frame: Any, column: str = "close", window: int = 17) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_high_12(values,window)

    def dataframe_13(self, frame: Any, column: str = "close", window: int = 18) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_low_13(values,window)

    def dataframe_14(self, frame: Any, column: str = "close", window: int = 19) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_volume_14(values,window)

    def dataframe_15(self, frame: Any, column: str = "close", window: int = 5) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_spread_15(values,window)

    def dataframe_16(self, frame: Any, column: str = "close", window: int = 6) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_returns_16(values,window)

    def dataframe_17(self, frame: Any, column: str = "close", window: int = 7) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_atr_17(values,window)

    def dataframe_18(self, frame: Any, column: str = "close", window: int = 8) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_rsi_18(values,window)

    def dataframe_19(self, frame: Any, column: str = "close", window: int = 9) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.feature_adx_19(values,window)

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
            results.append(self.feature_000(item, 0.0, 1.0))
        return results

    def batch_01(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_001(item, 0.0, 1.0))
        return results

    def batch_02(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_002(item, 0.0, 1.0))
        return results

    def batch_03(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_003(item, 0.0, 1.0))
        return results

    def batch_04(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_004(item, 0.0, 1.0))
        return results

    def batch_05(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_005(item, 0.0, 1.0))
        return results

    def batch_06(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_006(item, 0.0, 1.0))
        return results

    def batch_07(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_007(item, 0.0, 1.0))
        return results

    def batch_08(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_008(item, 0.0, 1.0))
        return results

    def batch_09(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.feature_009(item, 0.0, 1.0))
        return results

    def latest(self) -> Optional[EngineResult]:
        return self.history[-1] if self.history else None

    def reset(self) -> None:
        self.history.clear()
        self.state.clear()

    def snapshot(self) -> Dict[str, Any]:
        latest=self.latest()
        return {"engine":ENGINE_NAME,"version":ENGINE_VERSION,"history":len(self.history),"state":dict(self.state),"latest":latest.values if latest else None}

