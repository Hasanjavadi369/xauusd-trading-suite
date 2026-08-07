"""
کلاس پایه انتزاعی برای استراتژی‌ها. هر استراتژی جدید (کلاسیک، SMC، یا مبتنی بر AI
در آینده) باید از این کلاس ارث‌بری کند تا با موتور بک‌تست و اجرای زنده سازگار باشد.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd
from ..core.data_models import Signal


class BaseStrategy(ABC):
    name: str = "BaseStrategy"

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """محاسبه اندیکاتورها/ساختارهای لازم و برگرداندن دیتافریم غنی‌شده."""
        raise NotImplementedError

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """تولید لیست سیگنال‌های معاملاتی بر اساس دیتافریم آماده‌شده."""
        raise NotImplementedError

    def generate_latest_signal(self, df: pd.DataFrame) -> Optional[Signal]:
        """برای استفاده در حالت زنده: فقط آخرین سیگنال معتبر را برمی‌گرداند."""
        signals = self.generate_signals(df)
        return signals[-1] if signals else None
