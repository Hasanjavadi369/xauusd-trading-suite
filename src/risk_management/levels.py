"""Institutional-style entry/SL/TP level construction and validation.

The key rule is that risk is measured from the *actual entry price*, not from
an order-block edge. SL is structure/ATR based and TP is derived from the
validated risk distance. Broker minimum-stop distance can be applied later by
an execution adapter.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import math

from ..core.data_models import TradeDirection


@dataclass(frozen=True)
class TradeLevels:
    entry: float
    stop_loss: float
    take_profit: float
    risk_distance: float
    rr: float


def _finite(x: float) -> bool:
    return x is not None and math.isfinite(float(x))


def build_levels(
    direction: TradeDirection,
    entry_price: float,
    atr: float,
    zone_top: float,
    zone_bottom: float,
    rr_target: float = 2.0,
    atr_buffer_mult: float = 0.20,
    zone_buffer_pct: float = 0.10,
    min_risk_atr_mult: float = 0.50,
) -> Optional[TradeLevels]:
    """Build logically valid levels for a market/near-market entry.

    For LONG the structural invalidation is below the zone; for SHORT it is
    above the zone. If the zone is already on the wrong side of entry, the
    function falls back to an ATR stop rather than creating an invalid TP/SL.
    """
    vals = [entry_price, atr, zone_top, zone_bottom, rr_target]
    if not all(_finite(v) for v in vals) or atr <= 0 or rr_target <= 0:
        return None
    if zone_top < zone_bottom:
        zone_top, zone_bottom = zone_bottom, zone_top

    width = max(zone_top - zone_bottom, 0.0)
    buffer = max(atr * atr_buffer_mult, width * zone_buffer_pct)
    min_risk = atr * min_risk_atr_mult

    if direction == TradeDirection.LONG:
        structural_sl = zone_bottom - buffer
        fallback_sl = entry_price - min_risk
        stop = min(structural_sl, fallback_sl)
        risk = entry_price - stop
        if risk <= 0:
            stop = entry_price - max(atr, min_risk)
            risk = entry_price - stop
        tp = entry_price + risk * rr_target
    elif direction == TradeDirection.SHORT:
        structural_sl = zone_top + buffer
        fallback_sl = entry_price + min_risk
        stop = max(structural_sl, fallback_sl)
        risk = stop - entry_price
        if risk <= 0:
            stop = entry_price + max(atr, min_risk)
            risk = stop - entry_price
        tp = entry_price - risk * rr_target
    else:
        return None

    if not (_finite(stop) and _finite(tp) and risk > 0):
        return None
    return TradeLevels(
        entry=float(entry_price),
        stop_loss=float(stop),
        take_profit=float(tp),
        risk_distance=float(risk),
        rr=float(abs(tp - entry_price) / risk),
    )


def select_structural_target(
    direction: TradeDirection,
    entry: float,
    risk_distance: float,
    rr_target: float,
    candidates: list[float],
) -> float:
    """Choose the nearest opposing structural target that still satisfies RR.

    If no valid structural target exists, retain the configured RR target.
    """
    if risk_distance <= 0 or rr_target <= 0:
        return entry
    minimum_reward = risk_distance * rr_target
    if direction == TradeDirection.LONG:
        valid = [float(x) for x in candidates if _finite(x) and x >= entry + minimum_reward]
        return min(valid) if valid else entry + minimum_reward
    if direction == TradeDirection.SHORT:
        valid = [float(x) for x in candidates if _finite(x) and x <= entry - minimum_reward]
        return max(valid) if valid else entry - minimum_reward
    return entry


def validate_levels(direction: TradeDirection, entry: float, sl: float, tp: float, min_distance: float = 0.0):
    if not all(_finite(v) for v in (entry, sl, tp)):
        return False
    if direction == TradeDirection.LONG:
        return sl < entry - min_distance and tp > entry + min_distance
    if direction == TradeDirection.SHORT:
        return sl > entry + min_distance and tp < entry - min_distance
    return False
