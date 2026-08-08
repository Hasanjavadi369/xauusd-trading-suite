"""Phase 5 orchestration: validate -> features -> plan -> risk -> audit."""
from __future__ import annotations
from dataclasses import asdict
from typing import Sequence, Mapping, Any
from .core import clean_candles,snapshot,build_trade_plan,BrokerRules
from .validation import validate_ohlcv
from .risk import size_position,RiskConfig

class Phase5Engine:
    def __init__(self, config: Mapping[str,Any]|None=None):
        c=dict(config or {}); self.rules=BrokerRules(**dict(c.get("broker",{}))); self.risk=RiskConfig(**dict(c.get("risk",{})))
    def analyze(self, rows: Sequence[Mapping[str,Any]], side: str|None=None, equity: float|None=None, value_per_price_unit: float=1.0):
        report=validate_ohlcv(rows)
        if not report.valid: return {"valid":False,"validation":asdict(report)}
        candles=clean_candles(rows)
        if len(candles)<15: return {"valid":False,"reason":"insufficient clean candles","rows":len(candles)}
        s=snapshot(candles); direction=side or ("BUY" if s.trend>0 and s.momentum>=0 else "SELL" if s.trend<0 else "NEUTRAL")
        plan=build_trade_plan(s,direction,self.rules)
        out={"valid":plan.valid,"validation":asdict(report),"snapshot":asdict(s),"plan":asdict(plan)}
        if equity is not None and plan.valid: out["position_size"]=asdict(size_position(equity,plan.entry,plan.stop_loss,value_per_price_unit,self.risk))
        return out
