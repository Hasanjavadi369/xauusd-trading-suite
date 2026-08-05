"""
موتور بک‌تست: استراتژی (سیگنال‌های تولیدشده توسط src.strategy.signal_engine) را
روی داده‌های تاریخی کندلی اجرا می‌کند، معاملات را شبیه‌سازی می‌کند (با در نظر
گرفتن ریسک/سرمایه، تریلینگ استاپ و بریک‌ایون) و در پایان گزارش عملکرد می‌سازد.

این یک شبیه‌ساز ساده و قابل‌فهم (bar-by-bar, یک معامله در هر لحظه به ازای هر
جهت) است؛ برای بهینه‌سازی جدی‌تر (چند معامله همزمان، اسلیپیج پیشرفته، اجرای
اینترابار دقیق‌تر) می‌توان این موتور را گسترش داد.
"""
from __future__ import annotations

import itertools
import uuid
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional

import pandas as pd
from loguru import logger

from src.core.data_models import Signal, Trade, TradeDirection
from src.backtest.metrics import PerformanceReport, compute_performance
from src.risk_management.position_sizing import SymbolSpec, calculate_position_size
from src.risk_management.trade_manager import RiskConfig, TradeManager


@dataclass
class BacktestConfig:
    initial_balance: float = 10_000.0
    risk_percent_per_trade: float = 1.0
    spread_points: float = 20.0     # اسپرد فرضی به واحد قیمت (برای طلا مثلا ۰.۲۰ دلار)
    commission_per_lot: float = 0.0
    symbol_spec: SymbolSpec = None
    risk_config: RiskConfig = None

    def __post_init__(self):
        if self.symbol_spec is None:
            self.symbol_spec = SymbolSpec()
        if self.risk_config is None:
            self.risk_config = RiskConfig(risk_percent_per_trade=self.risk_percent_per_trade)


class BacktestEngine:
    """
    signal_fn: تابعی که یک DataFrame از داده‌ی تا لحظه فعلی (کندل بسته‌شده) می‌گیرد
               و در صورت وجود سیگنال، یک شیء Signal برمی‌گرداند (وگرنه None).
    """

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.trade_manager = TradeManager(self.config.risk_config)
        self.balance = self.config.initial_balance
        self.trades: List[Trade] = []
        self.open_trade: Optional[Trade] = None

    def run(
        self,
        df: pd.DataFrame,
        signal_fn: Callable[[pd.DataFrame], Optional[Signal]],
        atr_series: Optional[pd.Series] = None,
        warmup_bars: int = 100,
        signal_check_interval: int = 1,
    ) -> PerformanceReport:
        """
        signal_check_interval: هر چند کندل یک‌بار (وقتی معامله‌ای باز نیست) دنبال
            سیگنال جدید بگردد. مقدار ۱ = هر کندل (دقیق‌ترین اما کندتر روی
            تحلیل‌های سنگین SMC/ساختار بازار). برای دیتاست‌های بزرگ مقدار ۲ تا ۵
            سرعت را به‌شدت بالا می‌برد با از دست دادن جزئی دقت لحظه‌ی ورود.
        """
        """
        df: دیتافریم OHLCV با ایندکس datetime (ستون‌ها: open, high, low, close, volume)
        atr_series: مقدار ATR از پیش محاسبه‌شده هم‌طول با df (برای تریلینگ استاپ)
        """
        self.balance = self.config.initial_balance
        self.trades = []
        self.open_trade = None

        time_col = "time" if "time" in df.columns else None

        for i in range(warmup_bars, len(df)):
            window = df.iloc[: i + 1]
            bar = df.iloc[i]
            bar_time = bar[time_col] if time_col else bar.name
            atr_value = float(atr_series.iloc[i]) if atr_series is not None else 0.0

            # ۱) مدیریت معامله باز
            if self.open_trade is not None:
                self._process_open_trade(bar, bar_time, atr_value)

            # ۲) اگر معامله‌ای باز نیست، دنبال سیگنال جدید بگرد (با فاصله‌ی
            #    signal_check_interval کندل برای کنترل بار محاسباتی)
            if self.open_trade is None and (i % signal_check_interval == 0):
                signal = signal_fn(window)
                if signal is not None:
                    self._open_trade_from_signal(signal, bar_time)

        # بستن معامله باقی‌مانده در انتهای بازه با آخرین قیمت
        if self.open_trade is not None:
            last_bar = df.iloc[-1]
            last_time = last_bar[time_col] if time_col else last_bar.name
            self._close_trade(self.open_trade, last_bar["close"], last_time)

        return compute_performance(self.trades, self.config.initial_balance)

    # ------------------------------------------------------------------ #
    def _open_trade_from_signal(self, signal: Signal, timestamp) -> None:
        volume = calculate_position_size(
            account_balance=self.balance,
            risk_percent=self.config.risk_config.risk_percent_per_trade,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            symbol_spec=self.config.symbol_spec,
        )
        entry_price = signal.entry_price
        # شبیه‌سازی اسپرد ساده
        spread = self.config.spread_points * self.config.symbol_spec.tick_size
        if signal.direction == TradeDirection.LONG:
            entry_price += spread / 2
        else:
            entry_price -= spread / 2

        self.open_trade = Trade(
            id=str(uuid.uuid4())[:8],
            symbol="XAUUSD",
            direction=signal.direction,
            volume=volume,
            entry_price=entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            open_time=timestamp,
            tags=[s.value for s in signal.sources],
        )

    def _process_open_trade(self, bar: pd.Series, bar_time, atr_value: float) -> None:
        trade = self.open_trade
        high, low = bar["high"], bar["low"]

        # مدیریت بریک‌ایون/تریلینگ بر اساس قیمت close کندل
        trade = self.trade_manager.manage(trade, bar["close"], atr_value)
        self.open_trade = trade

        hit_sl = (low <= trade.stop_loss) if trade.direction == TradeDirection.LONG else (high >= trade.stop_loss)
        hit_tp = (high >= trade.take_profit) if trade.direction == TradeDirection.LONG else (low <= trade.take_profit)

        if hit_sl and hit_tp:
            # فرض محافظه‌کارانه: ابتدا استاپ لاس خورده باشد (بدترین حالت)
            self._close_trade(trade, trade.stop_loss, bar_time)
        elif hit_sl:
            self._close_trade(trade, trade.stop_loss, bar_time)
        elif hit_tp:
            self._close_trade(trade, trade.take_profit, bar_time)

    def _close_trade(self, trade: Trade, close_price: float, close_time) -> None:
        direction_mult = 1 if trade.direction == TradeDirection.LONG else -1
        price_diff = (close_price - trade.entry_price) * direction_mult
        contract_size = self.config.symbol_spec.contract_size
        profit = price_diff * trade.volume * contract_size
        profit -= self.config.commission_per_lot * trade.volume

        trade.close_price = close_price
        trade.close_time = close_time
        trade.profit = round(profit, 2)
        trade.is_open = False

        self.balance += trade.profit
        self.trades.append(trade)
        self.open_trade = None


def grid_search(
    df: pd.DataFrame,
    signal_fn_factory: Callable[..., Callable[[pd.DataFrame], Optional[Signal]]],
    param_grid: Dict[str, Iterable],
    atr_series: Optional[pd.Series] = None,
    base_config: Optional[BacktestConfig] = None,
) -> pd.DataFrame:
    """
    بهینه‌سازی ساده به روش Grid Search روی پارامترهای استراتژی.

    signal_fn_factory: تابعی که با گرفتن پارامترها، یک signal_fn برمی‌گرداند.
    param_grid: دیکشنری {نام پارامتر: لیست مقادیر ممکن}.
    """
    keys = list(param_grid.keys())
    combinations = list(itertools.product(*param_grid.values()))
    results = []

    for combo in combinations:
        params = dict(zip(keys, combo))
        engine = BacktestEngine(base_config)
        signal_fn = signal_fn_factory(**params)
        report = engine.run(df, signal_fn, atr_series=atr_series)
        row = {**params, **report.to_dict()}
        results.append(row)
        logger.info(f"پارامترها: {params} -> Net Profit: {report.net_profit}, Win Rate: {report.win_rate}%")

    return pd.DataFrame(results).sort_values(by="net_profit", ascending=False).reset_index(drop=True)
