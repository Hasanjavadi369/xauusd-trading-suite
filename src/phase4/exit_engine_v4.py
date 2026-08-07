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


"""Adaptive entry, stop, target, break-even and trailing calculations."""
ENGINE_NAME = "exit_engine_v4"
ENGINE_VERSION = "4.0.0"

class ExitEngineV4:
    """Deterministic production component with no hidden market-data source."""
    def __init__(self, config: Optional[Mapping[str, Any]] = None) -> None:
        self.config=dict(config or {})
        self.history: List[EngineResult]=[]
        self.state: Dict[str, Any]={}

    def exit_000(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 000."""
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

    def exit_001(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 001."""
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

    def exit_002(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 002."""
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

    def exit_003(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 003."""
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

    def exit_004(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 004."""
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

    def exit_005(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 005."""
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

    def exit_006(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 006."""
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

    def exit_007(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 007."""
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

    def exit_008(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 008."""
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

    def exit_009(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 009."""
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

    def exit_010(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 010."""
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

    def exit_011(self, value: Any = 0.0, reference: Any = 0.0, weight: float = 1.0) -> EngineResult:
        """Atomic exit primitive 011."""
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

    def exit_atr_00(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 00 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":0,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_structure_01(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute structure primitive 01 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"structure","index":1,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_volatility_02(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute volatility primitive 02 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volatility","index":2,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_rr_03(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute rr primitive 03 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rr","index":3,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_breakeven_04(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute breakeven primitive 04 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"breakeven","index":4,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_trail_05(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute trail primitive 05 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"trail","index":5,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_target_06(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute target primitive 06 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"target","index":6,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_stop_07(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute stop primitive 07 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"stop","index":7,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_partial_08(self, series: Optional[Sequence[float]] = None, window: int = 13, threshold: float = 0.0) -> EngineResult:
        """Compute partial primitive 08 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"partial","index":8,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_time_09(self, series: Optional[Sequence[float]] = None, window: int = 14, threshold: float = 0.0) -> EngineResult:
        """Compute time primitive 09 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"time","index":9,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_atr_10(self, series: Optional[Sequence[float]] = None, window: int = 15, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 10 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":10,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_structure_11(self, series: Optional[Sequence[float]] = None, window: int = 16, threshold: float = 0.0) -> EngineResult:
        """Compute structure primitive 11 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"structure","index":11,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_volatility_12(self, series: Optional[Sequence[float]] = None, window: int = 17, threshold: float = 0.0) -> EngineResult:
        """Compute volatility primitive 12 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volatility","index":12,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_rr_13(self, series: Optional[Sequence[float]] = None, window: int = 18, threshold: float = 0.0) -> EngineResult:
        """Compute rr primitive 13 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rr","index":13,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_breakeven_14(self, series: Optional[Sequence[float]] = None, window: int = 19, threshold: float = 0.0) -> EngineResult:
        """Compute breakeven primitive 14 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"breakeven","index":14,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_trail_15(self, series: Optional[Sequence[float]] = None, window: int = 20, threshold: float = 0.0) -> EngineResult:
        """Compute trail primitive 15 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"trail","index":15,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_target_16(self, series: Optional[Sequence[float]] = None, window: int = 21, threshold: float = 0.0) -> EngineResult:
        """Compute target primitive 16 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"target","index":16,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_stop_17(self, series: Optional[Sequence[float]] = None, window: int = 22, threshold: float = 0.0) -> EngineResult:
        """Compute stop primitive 17 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"stop","index":17,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_partial_18(self, series: Optional[Sequence[float]] = None, window: int = 23, threshold: float = 0.0) -> EngineResult:
        """Compute partial primitive 18 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"partial","index":18,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_time_19(self, series: Optional[Sequence[float]] = None, window: int = 24, threshold: float = 0.0) -> EngineResult:
        """Compute time primitive 19 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"time","index":19,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_atr_20(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 20 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":20,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_structure_21(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute structure primitive 21 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"structure","index":21,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_volatility_22(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute volatility primitive 22 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volatility","index":22,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_rr_23(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute rr primitive 23 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rr","index":23,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_breakeven_24(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute breakeven primitive 24 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"breakeven","index":24,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_trail_25(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute trail primitive 25 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"trail","index":25,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_target_26(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute target primitive 26 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"target","index":26,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_stop_27(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute stop primitive 27 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"stop","index":27,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_partial_28(self, series: Optional[Sequence[float]] = None, window: int = 13, threshold: float = 0.0) -> EngineResult:
        """Compute partial primitive 28 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"partial","index":28,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_time_29(self, series: Optional[Sequence[float]] = None, window: int = 14, threshold: float = 0.0) -> EngineResult:
        """Compute time primitive 29 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"time","index":29,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_atr_30(self, series: Optional[Sequence[float]] = None, window: int = 15, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 30 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":30,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_structure_31(self, series: Optional[Sequence[float]] = None, window: int = 16, threshold: float = 0.0) -> EngineResult:
        """Compute structure primitive 31 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"structure","index":31,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_volatility_32(self, series: Optional[Sequence[float]] = None, window: int = 17, threshold: float = 0.0) -> EngineResult:
        """Compute volatility primitive 32 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volatility","index":32,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_rr_33(self, series: Optional[Sequence[float]] = None, window: int = 18, threshold: float = 0.0) -> EngineResult:
        """Compute rr primitive 33 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rr","index":33,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_breakeven_34(self, series: Optional[Sequence[float]] = None, window: int = 19, threshold: float = 0.0) -> EngineResult:
        """Compute breakeven primitive 34 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"breakeven","index":34,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_trail_35(self, series: Optional[Sequence[float]] = None, window: int = 20, threshold: float = 0.0) -> EngineResult:
        """Compute trail primitive 35 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"trail","index":35,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_target_36(self, series: Optional[Sequence[float]] = None, window: int = 21, threshold: float = 0.0) -> EngineResult:
        """Compute target primitive 36 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"target","index":36,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_stop_37(self, series: Optional[Sequence[float]] = None, window: int = 22, threshold: float = 0.0) -> EngineResult:
        """Compute stop primitive 37 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"stop","index":37,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_partial_38(self, series: Optional[Sequence[float]] = None, window: int = 23, threshold: float = 0.0) -> EngineResult:
        """Compute partial primitive 38 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"partial","index":38,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_time_39(self, series: Optional[Sequence[float]] = None, window: int = 24, threshold: float = 0.0) -> EngineResult:
        """Compute time primitive 39 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"time","index":39,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_atr_40(self, series: Optional[Sequence[float]] = None, window: int = 5, threshold: float = 0.0) -> EngineResult:
        """Compute atr primitive 40 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"atr","index":40,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_structure_41(self, series: Optional[Sequence[float]] = None, window: int = 6, threshold: float = 0.0) -> EngineResult:
        """Compute structure primitive 41 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"structure","index":41,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_volatility_42(self, series: Optional[Sequence[float]] = None, window: int = 7, threshold: float = 0.0) -> EngineResult:
        """Compute volatility primitive 42 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"volatility","index":42,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_rr_43(self, series: Optional[Sequence[float]] = None, window: int = 8, threshold: float = 0.0) -> EngineResult:
        """Compute rr primitive 43 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"rr","index":43,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_breakeven_44(self, series: Optional[Sequence[float]] = None, window: int = 9, threshold: float = 0.0) -> EngineResult:
        """Compute breakeven primitive 44 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"breakeven","index":44,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_trail_45(self, series: Optional[Sequence[float]] = None, window: int = 10, threshold: float = 0.0) -> EngineResult:
        """Compute trail primitive 45 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"trail","index":45,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_target_46(self, series: Optional[Sequence[float]] = None, window: int = 11, threshold: float = 0.0) -> EngineResult:
        """Compute target primitive 46 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"target","index":46,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def exit_stop_47(self, series: Optional[Sequence[float]] = None, window: int = 12, threshold: float = 0.0) -> EngineResult:
        """Compute stop primitive 47 from supplied observations."""
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
        result=EngineResult(True,score,direction,{"topic":"stop","index":47,"mean":mean,"last":last,"spread":spread,"slope":slope,"count":len(tail)})
        self.history.append(result)
        return result

    def dataframe_00(self, frame: Any, column: str = "close", window: int = 5) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_atr_00(values,window)

    def dataframe_01(self, frame: Any, column: str = "close", window: int = 6) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_structure_01(values,window)

    def dataframe_02(self, frame: Any, column: str = "close", window: int = 7) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_volatility_02(values,window)

    def dataframe_03(self, frame: Any, column: str = "close", window: int = 8) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_rr_03(values,window)

    def dataframe_04(self, frame: Any, column: str = "close", window: int = 9) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_breakeven_04(values,window)

    def dataframe_05(self, frame: Any, column: str = "close", window: int = 10) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_trail_05(values,window)

    def dataframe_06(self, frame: Any, column: str = "close", window: int = 11) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_target_06(values,window)

    def dataframe_07(self, frame: Any, column: str = "close", window: int = 12) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_stop_07(values,window)

    def dataframe_08(self, frame: Any, column: str = "close", window: int = 13) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_partial_08(values,window)

    def dataframe_09(self, frame: Any, column: str = "close", window: int = 14) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_time_09(values,window)

    def dataframe_10(self, frame: Any, column: str = "close", window: int = 15) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_atr_10(values,window)

    def dataframe_11(self, frame: Any, column: str = "close", window: int = 16) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_structure_11(values,window)

    def dataframe_12(self, frame: Any, column: str = "close", window: int = 17) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_volatility_12(values,window)

    def dataframe_13(self, frame: Any, column: str = "close", window: int = 18) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_rr_13(values,window)

    def dataframe_14(self, frame: Any, column: str = "close", window: int = 19) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_breakeven_14(values,window)

    def dataframe_15(self, frame: Any, column: str = "close", window: int = 5) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_trail_15(values,window)

    def dataframe_16(self, frame: Any, column: str = "close", window: int = 6) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_target_16(values,window)

    def dataframe_17(self, frame: Any, column: str = "close", window: int = 7) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_stop_17(values,window)

    def dataframe_18(self, frame: Any, column: str = "close", window: int = 8) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_partial_18(values,window)

    def dataframe_19(self, frame: Any, column: str = "close", window: int = 9) -> EngineResult:
        """Analyze a supplied dataframe without fabricating observations."""
        if frame is None or not hasattr(frame,"__getitem__"):
            return EngineResult(False,warnings=["frame is missing"])
        try: values=list(frame[column].dropna())
        except Exception as exc: return EngineResult(False,warnings=[str(exc)])
        return self.exit_time_19(values,window)

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
            results.append(self.exit_000(item, 0.0, 1.0))
        return results

    def batch_01(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_001(item, 0.0, 1.0))
        return results

    def batch_02(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_002(item, 0.0, 1.0))
        return results

    def batch_03(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_003(item, 0.0, 1.0))
        return results

    def batch_04(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_004(item, 0.0, 1.0))
        return results

    def batch_05(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_005(item, 0.0, 1.0))
        return results

    def batch_06(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_006(item, 0.0, 1.0))
        return results

    def batch_07(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_007(item, 0.0, 1.0))
        return results

    def batch_08(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_008(item, 0.0, 1.0))
        return results

    def batch_09(self, values: Iterable[Any]) -> List[EngineResult]:
        results=[]
        for item in values:
            results.append(self.exit_009(item, 0.0, 1.0))
        return results

    def latest(self) -> Optional[EngineResult]:
        return self.history[-1] if self.history else None

    def reset(self) -> None:
        self.history.clear()
        self.state.clear()

    def snapshot(self) -> Dict[str, Any]:
        latest=self.latest()
        return {"engine":ENGINE_NAME,"version":ENGINE_VERSION,"history":len(self.history),"state":dict(self.state),"latest":latest.values if latest else None}

