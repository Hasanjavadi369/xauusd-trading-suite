"""
محاسبه حجم معامله (Position Sizing) بر اساس درصد ریسک حساب.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SymbolSpec:
    """مشخصات نماد لازم برای تبدیل پیپ/قیمت به سود و زیان."""
    contract_size: float = 100.0     # برای XAUUSD معمولا هر لات = ۱۰۰ اونس
    tick_size: float = 0.01
    tick_value: float = 1.0          # ارزش هر تیک به ازای ۱ لات، بر حسب ارز حساب
    volume_min: float = 0.01
    volume_max: float = 100.0
    volume_step: float = 0.01


def calculate_position_size(
    account_balance: float,
    risk_percent: float,
    entry_price: float,
    stop_loss: float,
    symbol_spec: SymbolSpec,
) -> float:
    """
    حجم معامله را طوری محاسبه می‌کند که در صورت برخورد به استاپ‌لاس،
    دقیقا risk_percent درصد از موجودی حساب از دست برود.
    """
    if account_balance <= 0 or risk_percent <= 0:
        return symbol_spec.volume_min

    risk_amount = account_balance * (risk_percent / 100.0)
    price_distance = abs(entry_price - stop_loss)
    if price_distance <= 0:
        return symbol_spec.volume_min

    ticks = price_distance / symbol_spec.tick_size
    loss_per_lot = ticks * symbol_spec.tick_value

    if loss_per_lot <= 0:
        return symbol_spec.volume_min

    raw_volume = risk_amount / loss_per_lot

    # گرد کردن به نزدیک‌ترین گام مجاز حجم
    steps = round(raw_volume / symbol_spec.volume_step)
    volume = steps * symbol_spec.volume_step
    volume = max(symbol_spec.volume_min, min(volume, symbol_spec.volume_max))
    return round(volume, 2)


def risk_reward_ratio(entry_price: float, stop_loss: float, take_profit: float) -> float:
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    return round(reward / risk, 2) if risk > 0 else 0.0
