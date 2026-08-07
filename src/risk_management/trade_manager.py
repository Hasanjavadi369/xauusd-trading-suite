"""
مدیریت زنده‌ی معاملات باز: Trailing Stop، Break Even و کنترل Max Drawdown.

این ماژول مستقل از MT5 است (فقط منطق را پیاده می‌کند) تا هم در بک‌تست
و هم در اجرای زنده (با فراخوانی connectors.mt5_connector) قابل استفاده باشد.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.core.data_models import Trade, TradeDirection


@dataclass
class RiskConfig:
    risk_percent_per_trade: float = 1.0
    max_daily_loss_percent: float = 3.0
    max_drawdown_percent: float = 10.0
    break_even_trigger_rr: float = 1.0       # وقتی سود به اندازه ۱ برابر ریسک رسید، استاپ به نقطه ورود منتقل شود
    trailing_start_rr: float = 1.5           # از این نسبت سود به بعد تریلینگ فعال می‌شود
    trailing_distance_atr_mult: float = 1.5  # فاصله‌ی تریلینگ بر اساس ضریبی از ATR


class TradeManager:
    """منطق مدیریت یک معامله‌ی باز را روی هر تیک/کندل جدید اعمال می‌کند."""

    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()

    def initial_risk(self, trade: Trade) -> float:
        return abs(trade.entry_price - trade.stop_loss)

    def current_rr(self, trade: Trade, current_price: float) -> float:
        risk = self.initial_risk(trade)
        if risk == 0:
            return 0.0
        direction_mult = 1 if trade.direction == TradeDirection.LONG else -1
        profit_distance = (current_price - trade.entry_price) * direction_mult
        return round(profit_distance / risk, 2)

    def apply_break_even(self, trade: Trade, current_price: float) -> Trade:
        if trade.break_even_applied:
            return trade
        if self.current_rr(trade, current_price) >= self.config.break_even_trigger_rr:
            trade.stop_loss = trade.entry_price
            trade.break_even_applied = True
        return trade

    def apply_trailing_stop(self, trade: Trade, current_price: float, atr_value: float) -> Trade:
        if self.current_rr(trade, current_price) < self.config.trailing_start_rr:
            return trade

        distance = atr_value * self.config.trailing_distance_atr_mult
        trade.trailing_stop_active = True

        if trade.direction == TradeDirection.LONG:
            new_sl = current_price - distance
            if new_sl > trade.stop_loss:
                trade.stop_loss = new_sl
        else:
            new_sl = current_price + distance
            if new_sl < trade.stop_loss:
                trade.stop_loss = new_sl
        return trade

    def manage(self, trade: Trade, current_price: float, atr_value: float) -> Trade:
        """یک‌جا بریک‌ایون و تریلینگ استاپ را روی معامله اعمال می‌کند."""
        trade = self.apply_break_even(trade, current_price)
        trade = self.apply_trailing_stop(trade, current_price, atr_value)
        return trade

    def should_stop_trading_today(self, daily_pnl_percent: float) -> bool:
        return daily_pnl_percent <= -abs(self.config.max_daily_loss_percent)

    def should_halt_all_trading(self, current_drawdown_percent: float) -> bool:
        return current_drawdown_percent >= abs(self.config.max_drawdown_percent)
