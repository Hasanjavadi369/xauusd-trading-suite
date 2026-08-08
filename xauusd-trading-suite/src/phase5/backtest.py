"""Event-driven, next-bar execution backtest with costs and deterministic fills."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Callable, Optional
import statistics

@dataclass(frozen=True)
class BacktestTrade:
    side:str; entry:float; exit:float; pnl:float; bars:int

@dataclass(frozen=True)
class BacktestReport:
    trades:tuple[BacktestTrade,...]
    net_pnl:float; win_rate:float; profit_factor:float; max_drawdown:float; expectancy:float

def run_next_bar(candles, signals: Sequence[Optional[str]], spread: float=0.0, commission: float=0.0,
                 hold_bars:int=1) -> BacktestReport:
    trades=[]; equity=0.0; peak=0.0; dd=0.0
    for i,side in enumerate(signals[:-1]):
        if side not in {"BUY","SELL"}: continue
        j=min(len(candles)-1,i+max(1,int(hold_bars)))
        entry=float(candles[i+1].open); exit=float(candles[j].close)
        cost=abs(float(spread))+abs(float(commission))
        pnl=(exit-entry if side=="BUY" else entry-exit)-cost
        trades.append(BacktestTrade(side,entry,exit,pnl,j-i)); equity+=pnl; peak=max(peak,equity); dd=max(dd,peak-equity)
    wins=[t.pnl for t in trades if t.pnl>0]; losses=[-t.pnl for t in trades if t.pnl<0]
    gross_loss=sum(losses); pf=sum(wins)/gross_loss if gross_loss else (float("inf") if wins else 0.0)
    return BacktestReport(tuple(trades),equity,len(wins)/len(trades) if trades else 0.0,pf,dd,statistics.fmean([t.pnl for t in trades]) if trades else 0.0)
