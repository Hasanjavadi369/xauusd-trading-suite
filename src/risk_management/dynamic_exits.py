"""ATR/structure based exit management for open trades."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ExitDecision:
    action: str
    new_stop: float | None = None
    reason: str = ""

def manage_exit(direction: str, entry: float, current: float, stop: float, atr: float,
                 rr_trigger: float=1.0, atr_trail: float=1.2, break_even_offset: float=0.0) -> ExitDecision:
    if atr <= 0: return ExitDecision("hold", reason="invalid_atr")
    risk=abs(entry-stop)
    if risk <= 0: return ExitDecision("hold", reason="invalid_risk")
    profit_dist=(current-entry) if direction=="LONG" else (entry-current)
    rr=profit_dist/risk
    if rr >= rr_trigger:
        be = entry + break_even_offset if direction=="LONG" else entry-break_even_offset
        trail = current-atr*atr_trail if direction=="LONG" else current+atr*atr_trail
        new = max(stop,be,trail) if direction=="LONG" else min(stop,be,trail)
        if (direction=="LONG" and new>stop) or (direction=="SHORT" and new<stop):
            return ExitDecision("modify_stop",float(new),f"rr={rr:.2f}")
    return ExitDecision("hold",reason=f"rr={rr:.2f}")
