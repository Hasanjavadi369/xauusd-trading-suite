"""
محاسبه معیارهای استاندارد ارزیابی استراتژی معاملاتی از روی لیست معاملات بسته‌شده.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

from src.core.data_models import Trade


@dataclass
class PerformanceReport:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    expectancy: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_percent: float = 0.0
    sharpe_ratio: float = 0.0
    equity_curve: pd.Series = field(default_factory=pd.Series)

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d.pop("equity_curve", None)
        return d


def compute_performance(trades: List[Trade], initial_balance: float = 10_000.0,
                         periods_per_year: int = 252) -> PerformanceReport:
    closed = [t for t in trades if not t.is_open and t.profit is not None]
    report = PerformanceReport()
    report.total_trades = len(closed)

    if not closed:
        report.equity_curve = pd.Series([initial_balance])
        return report

    profits = np.array([t.profit for t in closed], dtype=float)
    wins = profits[profits > 0]
    losses = profits[profits <= 0]

    report.winning_trades = len(wins)
    report.losing_trades = len(losses)
    report.win_rate = round(100 * len(wins) / len(closed), 2)
    report.gross_profit = round(float(wins.sum()), 2)
    report.gross_loss = round(float(losses.sum()), 2)
    report.net_profit = round(float(profits.sum()), 2)
    report.profit_factor = (
        round(abs(report.gross_profit / report.gross_loss), 2) if report.gross_loss != 0 else float("inf")
    )
    report.average_win = round(float(wins.mean()), 2) if len(wins) else 0.0
    report.average_loss = round(float(losses.mean()), 2) if len(losses) else 0.0
    report.expectancy = round(float(profits.mean()), 2)

    # Equity curve
    equity = initial_balance + np.cumsum(profits)
    equity_series = pd.Series(equity, index=[t.close_time for t in closed])
    report.equity_curve = equity_series

    # Max Drawdown
    running_max = np.maximum.accumulate(np.concatenate(([initial_balance], equity)))
    drawdowns = running_max - np.concatenate(([initial_balance], equity))
    report.max_drawdown = round(float(drawdowns.max()), 2)
    peak_at_max_dd = running_max[np.argmax(drawdowns)]
    report.max_drawdown_percent = round(100 * report.max_drawdown / peak_at_max_dd, 2) if peak_at_max_dd else 0.0

    # Sharpe Ratio (بر اساس بازده هر معامله، نه زمان تقویمی - تقریب ساده)
    returns = profits / initial_balance
    if returns.std(ddof=1) > 0:
        report.sharpe_ratio = round(
            float(np.sqrt(periods_per_year) * returns.mean() / returns.std(ddof=1)), 2
        )
    else:
        report.sharpe_ratio = 0.0

    return report
