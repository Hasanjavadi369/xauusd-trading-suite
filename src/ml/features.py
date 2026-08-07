"""
تعریف فیچرهای مدل امتیازدهی سیگنال (Signal Scoring Model).

نکته‌ی مهم و طراحی عمدی: این ماژول فقط اسکیمای فیچرها را نگه می‌دارد و هیچ
منطق محاسباتی مستقلی ندارد. مقادیر واقعی فیچرها همان‌جایی محاسبه می‌شوند که
سیگنال تولید می‌شود (``src/strategy/signal_engine.py``) و در
``Signal.metadata["features"]`` ذخیره می‌شوند. یعنی:

  1) این مدل هیچ داده‌ی جدیدی "پیش‌بینی نمی‌کند" — فقط از روی همان فیچرهایی
     که موتور SMC/اندیکاتورها از قبل تولید می‌کند (فاصله تا Order Block،
     قدرت FVG، هم‌جهتی چند اندیکاتور، ...) احتمال موفقیت را یاد می‌گیرد.
  2) چون فیچرهای آموزش (training) و فیچرهای استنتاج زنده (inference) دقیقاً
     از یک تابع مشترک می‌آیند، هیچ "train/serve skew" یا رفتار جعبه‌سیاه
     وجود ندارد — هر عدد در بردار فیچر قابل ردیابی به یک دلیل مشخص در
     ``signal.reasons`` است.

هر فیچر جدید که به موتور سیگنال اضافه می‌شود باید همزمان اینجا هم به
FEATURE_COLUMNS اضافه شود.
"""
from typing import Dict, List

# ترتیب ستون‌ها باید ثابت بماند (هم برای آموزش و هم برای استنتاج).
FEATURE_COLUMNS: List[str] = [
    "ob_strength",           # قدرت ایمپالسی که Order Block را تشکیل داد (بدنه‌ی کندل ایمپالس / ATR)
    "ob_width_atr",          # عرض ناحیه‌ی Order Block نسبت به ATR لحظه‌ی سیگنال
    "trend_aligned",         # هم‌جهتی با روند غالب ساختار بازار (BOS/CHOCH) — ۰/۱
    "fvg_confluence",        # همپوشانی با یک Fair Value Gap هم‌جهت — ۰/۱
    "fvg_strength",          # بیشینه‌ی درصد شکاف FVGهای هم‌پوشان (۰ اگر همپوشانی نبود)
    "candle_confirmation",   # تایید الگوی کندلی (پین‌بار/انگالفینگ هم‌جهت) — ۰/۱
    "rsi_value",             # مقدار RSI در کندل سیگنال
    "rsi_confirmation",      # RSI در ناحیه‌ی هم‌جهت با سیگنال (اشباع خرید/فروش نسبی) — ۰/۱
    "supertrend_aligned",    # هم‌جهتی SuperTrend با سیگنال — ۰/۱
    "adx_value",             # قدرت روند (ADX) در کندل سیگنال
    "macd_hist",             # هیستوگرام MACD در کندل سیگنال
    "bb_position",           # موقعیت close نسبت به باندهای بولینگر (۰=باند پایین، ۱=باند بالا)
    "atr_pct",               # نوسان نرمال‌شده: ATR / close
    "liquidity_sweep_nearby",  # آیا اخیراً یک Liquidity Sweep هم‌جهت رخ داده — ۰/۱
    "sr_confluence",         # همپوشانی ناحیه‌ی سیگنال با یک سطح حمایت/مقاومت شناخته‌شده — ۰/۱
    "n_confluences",         # تعداد کل دلایل/منابع تاییدکننده‌ی سیگنال (طول sources)
    "risk_reward",           # نسبت ریوارد به ریسک هدف سیگنال
    "rule_confidence",       # امتیاز اطمینان قانون‌محور (confidence) نرمال‌شده به ۰..۱
]


def empty_feature_row() -> Dict[str, float]:
    """یک بردار فیچر صفر (fallback امن برای زمانی که محاسبه‌ی فیچر ممکن نبود)."""
    return {col: 0.0 for col in FEATURE_COLUMNS}


def feature_dict_to_row(features: Dict[str, float]) -> Dict[str, float]:
    """فیچرهای ذخیره‌شده روی یک سیگنال را به بردار کامل و مرتب (طبق FEATURE_COLUMNS) تبدیل می‌کند."""
    row = empty_feature_row()
    for key in FEATURE_COLUMNS:
        if key in features and features[key] is not None:
            row[key] = float(features[key])
    return row
