"""
مدل‌های داده مشترک پروژه.

این ماژول ساختارهای داده‌ای اصلی (سیگنال، معامله، موقعیت باز) را تعریف می‌کند
که در تمام ماژول‌های دیگر (strategy، risk_management، backtest، chart) استفاده می‌شوند.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class TradeDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


class SignalSource(str, Enum):
    ORDER_BLOCK = "ORDER_BLOCK"
    FVG = "FVG"
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP"
    BOS = "BOS"
    CHOCH = "CHOCH"
    SUPPLY_DEMAND = "SUPPLY_DEMAND"
    SUPPORT_RESISTANCE = "SUPPORT_RESISTANCE"
    CANDLESTICK_PATTERN = "CANDLESTICK_PATTERN"
    INDICATOR_CONFLUENCE = "INDICATOR_CONFLUENCE"


@dataclass
class Signal:
    """یک سیگنال معاملاتی پیشنهادی که موتور استراتژی تولید می‌کند."""
    timestamp: datetime
    direction: TradeDirection
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float                 # امتیاز اطمینان ۰ تا ۱۰۰
    sources: List[SignalSource] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)   # توضیح متنی دلایل سیگنال
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def risk_reward(self) -> float:
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        if risk == 0:
            return 0.0
        return round(reward / risk, 2)


@dataclass
class Trade:
    """یک معامله اجرا شده (باز یا بسته)."""
    id: str
    symbol: str
    direction: TradeDirection
    volume: float
    entry_price: float
    stop_loss: float
    take_profit: float
    open_time: datetime
    close_time: Optional[datetime] = None
    close_price: Optional[float] = None
    profit: Optional[float] = None
    is_open: bool = True
    break_even_applied: bool = False
    trailing_stop_active: bool = False
    tags: List[str] = field(default_factory=list)

    def unrealized_pnl(self, current_price: float, pip_value: float = 1.0) -> float:
        direction_mult = 1 if self.direction == TradeDirection.LONG else -1
        return (current_price - self.entry_price) * direction_mult * self.volume * pip_value


@dataclass
class MarketStructurePoint:
    """نقطه‌ی ساختار بازار (Swing High/Low, BOS, CHOCH)."""
    timestamp: datetime
    price: float
    kind: str          # "swing_high", "swing_low", "BOS", "CHOCH"
    index: int


@dataclass
class Zone:
    """ناحیه‌ی قیمتی عمومی برای Order Block / FVG / Supply-Demand / Liquidity."""
    kind: str           # "order_block_bullish", "fvg_bearish", ...
    start_time: datetime
    end_time: Optional[datetime]
    top: float
    bottom: float
    mitigated: bool = False
    strength: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
