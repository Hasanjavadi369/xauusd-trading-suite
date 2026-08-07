"""
حساب دمو داخلی (Paper Trading).

این ماژول یک حساب معاملاتی کاملاً شبیه‌سازی‌شده و بدون نیاز به اتصال به بروکر
پیاده‌سازی می‌کند: موجودی (Balance)، دارایی (Equity)، مارجین/مارجین آزاد، سود و
زیان لحظه‌ای، و تاریخچه‌ی کامل معاملات باز/بسته. برای اجرای معاملات خودکار
موتور تحلیل هوش مصنوعی (AutoTrader) و نمایش در تب «حساب دمو» داشبورد استفاده می‌شود.

طراحی عمداً ساده و بدون وابستگی به دیتابیس است؛ وضعیت در session_state استریملیت
نگه‌داری می‌شود (هر کاربر/سشن حساب دمو مستقل خودش را دارد).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from ..core.data_models import Trade, TradeDirection
from ..risk_management.position_sizing import SymbolSpec


@dataclass
class DemoAccount:
    """حساب دمو با موجودی اولیه‌ی قابل‌تنظیم (پیش‌فرض ۱۰,۰۰۰ دلار)."""

    initial_balance: float = 10_000.0
    symbol: str = "XAUUSD"
    symbol_spec: SymbolSpec = field(default_factory=SymbolSpec)
    leverage: float = 100.0

    balance: float = field(init=False)
    open_trades: List[Trade] = field(default_factory=list, init=False)
    closed_trades: List[Trade] = field(default_factory=list, init=False)
    _trade_counter: int = field(default=0, init=False)

    def __post_init__(self):
        self.balance = self.initial_balance

    # ------------------------------------------------------------------ #
    # بازنشانی
    # ------------------------------------------------------------------ #
    def reset(self, initial_balance: Optional[float] = None) -> None:
        if initial_balance is not None:
            self.initial_balance = initial_balance
        self.balance = self.initial_balance
        self.open_trades = []
        self.closed_trades = []
        self._trade_counter = 0

    # ------------------------------------------------------------------ #
    # باز کردن / بستن معامله
    # ------------------------------------------------------------------ #
    def open_trade(
        self,
        direction: TradeDirection,
        volume: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        open_time: datetime,
        confidence: Optional[float] = None,
        ml_probability: Optional[float] = None,
        tags: Optional[List[str]] = None,
        features: Optional[dict] = None,
    ) -> Trade:
        self._trade_counter += 1
        trade = Trade(
            id=f"DEMO-{self._trade_counter:05d}",
            symbol=self.symbol,
            direction=direction,
            volume=volume,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            open_time=open_time,
            is_open=True,
            tags=list(tags or []),
            metadata={"features": features, "ml_probability": ml_probability},
        )
        # اطمینان/امتیاز ML را برای نمایش بعدی نگه می‌داریم (بدون نیاز به تغییر مدل Trade اصلی)
        trade.tags.append(f"conf={confidence:.0f}" if confidence is not None else "conf=?")
        if ml_probability is not None:
            trade.tags.append(f"ml={ml_probability:.2f}")
        self.open_trades.append(trade)
        return trade

    def trade_pnl(self, trade: Trade, price: float) -> float:
        """سود/زیان شناور یک معامله‌ی مشخص در قیمت داده‌شده (برای نمایش در جدول معاملات باز)."""
        return self._pnl(trade, price)

    def _pnl(self, trade: Trade, price: float) -> float:
        direction_mult = 1 if trade.direction == TradeDirection.LONG else -1
        price_diff = (price - trade.entry_price) * direction_mult
        ticks = price_diff / self.symbol_spec.tick_size
        return round(ticks * self.symbol_spec.tick_value * trade.volume, 2)

    def mark_to_market(self, high: float, low: float, close: float, current_time: datetime) -> List[Trade]:
        """
        معاملات باز را نسبت به آخرین کندل (High/Low) بررسی می‌کند و در صورت برخورد
        به SL یا TP، آن‌ها را می‌بندد. لیست معاملاتی که در همین فراخوانی بسته شدند
        را برمی‌گرداند. اگر در یک کندل هم SL و هم TP قابل لمس باشند، به‌صورت
        محافظه‌کارانه فرض می‌شود ابتدا SL خورده است.
        """
        closed_now: List[Trade] = []
        still_open: List[Trade] = []
        for trade in self.open_trades:
            hit_reason = None
            hit_price = None
            if trade.direction == TradeDirection.LONG:
                if low <= trade.stop_loss:
                    hit_reason, hit_price = "SL", trade.stop_loss
                elif high >= trade.take_profit:
                    hit_reason, hit_price = "TP", trade.take_profit
            else:
                if high >= trade.stop_loss:
                    hit_reason, hit_price = "SL", trade.stop_loss
                elif low <= trade.take_profit:
                    hit_reason, hit_price = "TP", trade.take_profit

            if hit_reason:
                trade.close_time = current_time
                trade.close_price = hit_price
                trade.profit = self._pnl(trade, hit_price)
                trade.is_open = False
                trade.tags.append(hit_reason)
                self.balance += trade.profit
                closed_now.append(trade)
                self.closed_trades.append(trade)
            else:
                still_open.append(trade)

        self.open_trades = still_open
        return closed_now

    def close_trade_manual(self, trade_id: str, current_price: float, current_time: datetime) -> Optional[Trade]:
        for i, trade in enumerate(self.open_trades):
            if trade.id == trade_id:
                trade.close_time = current_time
                trade.close_price = current_price
                trade.profit = self._pnl(trade, current_price)
                trade.is_open = False
                trade.tags.append("MANUAL")
                self.balance += trade.profit
                self.closed_trades.append(trade)
                del self.open_trades[i]
                return trade
        return None

    # ------------------------------------------------------------------ #
    # متریک‌های حساب
    # ------------------------------------------------------------------ #
    def floating_pnl(self, current_price: float) -> float:
        return round(sum(self._pnl(t, current_price) for t in self.open_trades), 2)

    def equity(self, current_price: float) -> float:
        return round(self.balance + self.floating_pnl(current_price), 2)

    def used_margin(self) -> float:
        total = 0.0
        for t in self.open_trades:
            notional = t.entry_price * self.symbol_spec.contract_size * t.volume
            total += notional / max(self.leverage, 1.0)
        return round(total, 2)

    def free_margin(self, current_price: float) -> float:
        return round(self.equity(current_price) - self.used_margin(), 2)

    def win_rate(self) -> float:
        closed = self.closed_trades
        if not closed:
            return 0.0
        wins = sum(1 for t in closed if (t.profit or 0) > 0)
        return round(wins / len(closed) * 100, 1)

    def max_drawdown_percent(self, current_price: float) -> float:
        curve = self.equity_curve(current_price)
        if not curve:
            return 0.0
        peak = curve[0]
        worst = 0.0
        for v in curve:
            peak = max(peak, v)
            if peak > 0:
                dd = (peak - v) / peak * 100
                worst = max(worst, dd)
        return round(worst, 2)

    def realized_pnl_since(self, since_dt: datetime) -> float:
        return round(
            sum(t.profit for t in self.closed_trades if t.close_time and t.close_time >= since_dt and t.profit),
            2,
        )

    def pnl_today(self, now: datetime) -> float:
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.realized_pnl_since(start_of_day)

    def pnl_last_days(self, now: datetime, days: int) -> float:
        return self.realized_pnl_since(now - timedelta(days=days))

    def daily_loss_percent(self, now: datetime) -> float:
        """درصد ضرر تحقق‌یافته‌ی امروز نسبت به موجودی اولیه (برای توقف خودکار)."""
        if self.initial_balance <= 0:
            return 0.0
        pnl = self.pnl_today(now)
        return round(pnl / self.initial_balance * 100, 2)

    def equity_curve(self, current_price: Optional[float] = None) -> List[float]:
        curve = [self.initial_balance]
        running = self.initial_balance
        for t in sorted((tr for tr in self.closed_trades if tr.close_time), key=lambda x: x.close_time):
            running += t.profit or 0.0
            curve.append(round(running, 2))
        if current_price is not None:
            curve.append(self.equity(current_price))
        return curve
