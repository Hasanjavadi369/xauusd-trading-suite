"""
منطق تصمیم‌گیری معاملات خودکار: آیا سیگنال فعلی برای ورود خودکار به معامله در
حساب دمو، به‌اندازه‌ی کافی «مطمئن» است یا نه.

این ماژول عمداً خیلی کوچک و بدون وابستگی به Streamlit است تا قابل تست باشد.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..core.data_models import Signal


@dataclass
class AutoTradeConfig:
    enabled: bool = False
    min_confidence_pct: float = 70.0     # حداقل درصد موفقیت/اطمینان برای ورود
    prefer_ml_score: bool = True         # اگر امتیاز ML موجود بود، به‌جای confidence قانون‌محور از آن استفاده شود
    max_open_trades: int = 3
    max_daily_loss_pct: float = 3.0


def effective_confidence(signal: Signal, prefer_ml_score: bool) -> float:
    """درصد اطمینان مؤثر سیگنال را برمی‌گرداند (۰ تا ۱۰۰)."""
    if prefer_ml_score and signal.ml_probability is not None:
        return signal.ml_probability * 100.0
    return signal.confidence


def decide_auto_entry(
    signal: Optional[Signal],
    cfg: AutoTradeConfig,
    current_open_trades: int,
    daily_loss_pct: float,
) -> bool:
    """
    True برمی‌گرداند اگر و فقط اگر همه‌ی شرایط زیر برقرار باشند:
    - معاملات خودکار فعال است
    - یک سیگنال معتبر وجود دارد
    - تعداد معاملات باز از سقف مجاز کمتر است
    - به حد ضرر روزانه نرسیده‌ایم
    - درصد اطمینان مؤثر سیگنال >= آستانه‌ی کاربر
    """
    if not cfg.enabled or signal is None:
        return False
    if current_open_trades >= cfg.max_open_trades:
        return False
    if daily_loss_pct <= -abs(cfg.max_daily_loss_pct):
        return False
    conf = effective_confidence(signal, cfg.prefer_ml_score)
    return conf >= cfg.min_confidence_pct
