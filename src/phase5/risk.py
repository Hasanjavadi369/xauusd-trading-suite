"""Capital and position sizing with explicit monetary risk constraints."""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class RiskConfig:
    risk_fraction: float=0.01
    max_position_fraction: float=1.0
    min_lot: float=0.01
    max_lot: float=100.0
    lot_step: float=0.01

@dataclass(frozen=True)
class PositionSize:
    lots: float
    risk_money: float
    risk_fraction: float
    valid: bool
    reason: str=""

def size_position(equity: float, entry: float, stop: float, value_per_price_unit: float,
                  cfg: RiskConfig=RiskConfig()) -> PositionSize:
    equity=float(equity); distance=abs(float(entry)-float(stop)); vpu=float(value_per_price_unit)
    if equity<=0 or distance<=0 or vpu<=0: return PositionSize(0,0,0,False,"invalid sizing inputs")
    rf=max(0.0,min(float(cfg.risk_fraction),float(cfg.max_position_fraction)))
    money=equity*rf; raw=money/(distance*vpu)
    step=max(float(cfg.lot_step),1e-12)
    lots=math.floor(raw/step)*step
    lots=max(0.0,min(float(cfg.max_lot),lots))
    if lots<float(cfg.min_lot): return PositionSize(0,0,0,False,"minimum lot exceeds risk budget")
    return PositionSize(round(lots,8),lots*distance*vpu,lots*distance*vpu/equity,True)
