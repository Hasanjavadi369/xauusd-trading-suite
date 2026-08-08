"""Execution guards: validate a signal against broker/market constraints before sending."""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class ExecutionConstraints:
    digits: int = 2
    point: float = 0.01
    stops_level_points: int = 0
    freeze_level_points: int = 0
    max_spread_points: int = 0

@dataclass(frozen=True)
class ExecutionCheck:
    ok: bool
    reason: str
    entry: float
    sl: float
    tp: float
    spread_points: float

def normalize_price(price: float, digits: int) -> float:
    if not math.isfinite(price): raise ValueError("non-finite price")
    return round(float(price), int(digits))

def validate_execution(direction: str, bid: float, ask: float, sl: float, tp: float,
                       constraints: ExecutionConstraints) -> ExecutionCheck:
    if bid <= 0 or ask <= 0 or ask < bid: return ExecutionCheck(False,"invalid_quote",0,0,0,0)
    entry = ask if direction == "LONG" else bid
    spread = (ask-bid)/constraints.point if constraints.point > 0 else 0
    min_dist = max(constraints.stops_level_points, constraints.freeze_level_points)*constraints.point
    if constraints.max_spread_points and spread > constraints.max_spread_points:
        return ExecutionCheck(False,"spread_too_high",entry,sl,tp,spread)
    if direction == "LONG" and not (sl < entry-min_dist and tp > entry+min_dist):
        return ExecutionCheck(False,"invalid_long_levels",entry,sl,tp,spread)
    if direction == "SHORT" and not (sl > entry+min_dist and tp < entry-min_dist):
        return ExecutionCheck(False,"invalid_short_levels",entry,sl,tp,spread)
    return ExecutionCheck(True,"ok",entry,normalize_price(sl,constraints.digits),normalize_price(tp,constraints.digits),spread)
