"""
برچسب‌گذاری داده برای یادگیری نظارت‌شده با روش Triple-Barrier
(الهام‌گرفته از روش استاندارد Marcos López de Prado):

برای هر کندل i، دو سطح تعریف می‌شود:
  - سقف (Take-Profit فرضی): close[i] + tp_atr_mult * ATR[i]
  - کف (Stop-Loss فرضی):   close[i] - sl_atr_mult * ATR[i]

سپس تا `max_horizon_bars` کندل بعدی بررسی می‌شود کدام سطح زودتر لمس می‌شود:
  +1  : سقف زودتر لمس شد (رفتار صعودی محتمل)
  -1  : کف زودتر لمس شد (رفتار نزولی محتمل)
   0  : هیچ‌کدام تا پایان افق زمانی لمس نشد (خنثی/بدون حرکت قابل توجه)

این برچسب مستقیماً از رفتار آینده‌ی قیمت (نه از قوانین SMC) ساخته می‌شود، بنابراین
مدلی که روی آن آموزش می‌بیند، «رفتار قیمت» را یاد می‌گیرد نه قوانین از پیش تعریف‌شده.
"""
import numpy as np
import pandas as pd


def triple_barrier_labels(df: pd.DataFrame, atr: pd.Series,
                           tp_atr_mult: float = 2.0, sl_atr_mult: float = 1.0,
                           max_horizon_bars: int = 20) -> pd.Series:
    n = len(df)
    labels = np.full(n, np.nan)

    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    atr_vals = atr.values

    for i in range(n - 1):
        a = atr_vals[i]
        if np.isnan(a) or a <= 0:
            continue

        entry = close[i]
        tp_level = entry + tp_atr_mult * a
        sl_level = entry - sl_atr_mult * a

        end = min(i + 1 + max_horizon_bars, n)
        label = 0.0
        for j in range(i + 1, end):
            hit_tp = high[j] >= tp_level
            hit_sl = low[j] <= sl_level
            if hit_tp and hit_sl:
                # هر دو در یک کندل لمس شدند؛ محافظه‌کارانه فرض می‌کنیم SL زودتر خورده (نامعلوم بودن ترتیب درون‌کندلی)
                label = -1.0
                break
            if hit_tp:
                label = 1.0
                break
            if hit_sl:
                label = -1.0
                break
        labels[i] = label

    return pd.Series(labels, index=df.index, name="label")


def label_distribution(labels: pd.Series) -> dict:
    valid = labels.dropna()
    counts = valid.value_counts(normalize=True).to_dict()
    return {
        "bullish_pct": round(counts.get(1.0, 0.0) * 100, 2),
        "bearish_pct": round(counts.get(-1.0, 0.0) * 100, 2),
        "neutral_pct": round(counts.get(0.0, 0.0) * 100, 2),
        "total_labeled": int(valid.count()),
    }
