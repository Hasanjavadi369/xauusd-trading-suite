"""
ماژول یادگیری ماشین XAUUSD Trading Suite.

این پکیج یک "مدل امتیازدهی سیگنال" (Signal Scoring Model) پیاده می‌کند، **نه**
یک مدل پیش‌بینی قیمت. ورودی مدل همان فیچرهای قابل‌مشاهده‌ی موتور SMC/اندیکاتور
است (فاصله/قدرت Order Block، همپوشانی FVG، هم‌جهتی چند اندیکاتور، ...) و خروجی
آن احتمال این است که یک سیگنال مشخص به Take Profit برسد قبل از آنکه Stop Loss
بخورد. کاملاً روی داده‌ی تاریخی خودِ پروژه train می‌شود و تفسیرپذیر است
(feature importance در دسترس است) — یعنی جعبه‌سیاه نیست.

اجزا:
    features.py -> اسکیمای مشترک فیچرها (استفاده‌شده هم در آموزش هم در inference)
    dataset.py   -> ساخت دیتاست برچسب‌خورده از داده‌ی تاریخی (walk-forward)
    scorer.py    -> کلاس SignalScorer (train/predict/save/load)
"""
from .scorer import SignalScorer
from .features import FEATURE_COLUMNS

__all__ = ["SignalScorer", "FEATURE_COLUMNS"]
