"""
ساخت دیتاست آموزشی برای مدل امتیازدهی سیگنال.

روش کار عمداً دقیقاً مثل نحوه‌ی مصرف سیگنال در بک‌تست/زنده (به src.backtest.engine
و src.main.run_backtest نگاه کنید) است: در هر کندل بسته‌شده، اگر معامله‌ی بازی
وجود نداشته باشد، از استراتژی برای یک پنجره‌ی اخیر (``analysis_window_bars``)
یک سیگنال خواسته می‌شود. اگر سیگنالی بیاید، از همان لحظه (نه لحظه‌ی شکل‌گیری
Order Block) به بعد دنبال می‌کنیم که آیا TP یا SL زودتر لمس می‌شود. این هم‌ترازی
عمدی بین «نحوه‌ی تولید دیتاست» و «نحوه‌ی مصرف واقعی سیگنال» باعث می‌شود مدل روی
همان توزیعی train شود که در inference واقعی می‌بیند (بدون train/serve skew).

برچسب (label):
  1  -> Take Profit قبل از Stop Loss لمس شد (سیگنال «برنده»)
  0  -> Stop Loss لمس شد (یا هر دو در یک کندل لمس شدند؛ طبق قرارداد محافظه‌کارانه‌ی
        همین پروژه در BacktestEngine._process_open_trade، این حالت هم باخت حساب می‌شود)
  سیگنال‌هایی که تا افق زمانی max_horizon_bars به هیچ‌کدام نرسند، از دیتاست حذف
  می‌شوند (نه برد نه باخت — داده‌ی ناقص است).
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from ..core.data_models import TradeDirection
from ..strategy.signal_engine import SMCConfluenceStrategy
from .features import feature_dict_to_row, FEATURE_COLUMNS


def build_training_dataset(
    df: pd.DataFrame,
    strategy: SMCConfluenceStrategy,
    analysis_window_bars: int = 200,
    check_interval: int = 3,
    warmup_bars: int = 100,
    max_horizon_bars: int = 200,
) -> pd.DataFrame:
    """
    df: دیتافریم OHLCV کامل که از قبل اندیکاتورها روی آن محاسبه شده
        (خروجی compute_all_indicators) و از strategy.prepare() عبور کرده باشد.
    strategy: نمونه‌ی SMCConfluenceStrategy **بدون** scorer (چون هدف ساخت دیتاست
        برای آموزش خودِ scorer است؛ اگر scorer از قبل ست شده باشد فقط نادیده
        گرفته می‌شود چون فقط از generate_latest_signal برای فیچرها و SL/TP استفاده می‌کنیم).

    خروجی: DataFrame با ستون‌های FEATURE_COLUMNS + label + چند ستون کمکی
        (timestamp, direction, rule_confidence_pct) برای دیباگ/تحلیل.
    """
    rows = []
    n = len(df)
    open_signal = None
    open_idx: Optional[int] = None

    i = warmup_bars
    while i < n:
        if open_signal is not None:
            bar = df.iloc[i]
            is_long = open_signal.direction == TradeDirection.LONG
            hit_sl = (bar["low"] <= open_signal.stop_loss) if is_long else (bar["high"] >= open_signal.stop_loss)
            hit_tp = (bar["high"] >= open_signal.take_profit) if is_long else (bar["low"] <= open_signal.take_profit)

            label = None
            resolved = False
            if hit_sl:  # قرارداد محافظه‌کارانه: اگر هر دو در یک کندل لمس شدند، SL برنده است
                label, resolved = 0, True
            elif hit_tp:
                label, resolved = 1, True
            elif (i - open_idx) >= max_horizon_bars:
                resolved = True  # ناتمام -> دور ریخته می‌شود (label می‌ماند None)

            if resolved:
                if label is not None:
                    feat_row = feature_dict_to_row(open_signal.metadata.get("features", {}))
                    feat_row["label"] = label
                    feat_row["timestamp"] = open_signal.timestamp
                    feat_row["direction"] = open_signal.direction.value
                    feat_row["rule_confidence_pct"] = open_signal.confidence
                    rows.append(feat_row)
                open_signal = None
                open_idx = None
            i += 1
            continue

        if i % check_interval == 0:
            window = df.iloc[: i + 1]
            recent = window.iloc[-analysis_window_bars:] if len(window) > analysis_window_bars else window
            signal = strategy.generate_latest_signal(recent)
            if signal is not None:
                open_signal = signal
                open_idx = i
        i += 1

    columns = FEATURE_COLUMNS + ["label", "timestamp", "direction", "rule_confidence_pct"]
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows)[columns]
