"""Walk-forward evaluation with chronological train/test windows."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from .engine import BacktestEngine, BacktestConfig

@dataclass(frozen=True)
class WalkForwardResult:
    folds: int
    reports: list[dict]
    aggregate_net_profit: float
    aggregate_trades: int

def run_walk_forward(df: pd.DataFrame, signal_fn_factory, train_bars: int=500, test_bars: int=200,
                     step: int|None=None, config: BacktestConfig|None=None) -> WalkForwardResult:
    step=step or test_bars
    reports=[]
    start=train_bars
    while start+test_bars <= len(df):
        train=df.iloc[:start].copy()
        test=df.iloc[start:start+test_bars].copy()
        signal_fn=signal_fn_factory(train)
        report=BacktestEngine(config).run(test,signal_fn)
        reports.append(report.to_dict())
        start += step
    return WalkForwardResult(len(reports),reports,
        float(sum(r.get("net_profit",0) for r in reports)),
        int(sum(r.get("total_trades",r.get("trades",0)) for r in reports)))
