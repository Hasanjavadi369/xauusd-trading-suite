"""
تولید یک فایل CSV نمونه (شبیه‌سازی‌شده، نه واقعی) از داده‌های ساعتی XAUUSD
برای تست سریع بک‌تست و چارت بدون نیاز به اتصال زنده به MT5.

اجرا:
    python scripts/generate_sample_data.py --bars 3000 --out data/sample_xauusd_h1.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def generate(bars: int = 3000, start_price: float = 2350.0, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dt_index = pd.date_range(end=pd.Timestamp.utcnow().floor("h"), periods=bars, freq="h")

    # حرکت قیمت با یک مؤلفه روند + نویز تصادفی (Random Walk) + چند شوک نوسانی
    drift = rng.normal(0, 0.5, size=bars).cumsum() * 0.05
    noise = rng.normal(0, 1.2, size=bars)
    shocks = np.where(rng.random(bars) < 0.02, rng.normal(0, 6, size=bars), 0)
    base_close = start_price + drift + noise.cumsum() * 0.1 + shocks.cumsum() * 0.05

    # ضربه‌های تک‌کندلی قوی (شبیه‌سازی حرکات ایمپالسیو/نیوز طلا) تا Order Block
    # و FVG واقعی در داده نمونه شکل بگیرد
    impulse_mask = rng.random(bars) < 0.035
    impulse_size = rng.normal(0, 9.0, size=bars) * impulse_mask

    highs, lows, opens, closes = [], [], [], []
    prev_close = start_price
    for i in range(bars):
        o = prev_close + rng.normal(0, 0.3)
        c = base_close[i] + impulse_size[i]
        spread = abs(rng.normal(1.5, 0.8)) + 0.3
        h = max(o, c) + abs(rng.normal(0.5, 0.4)) + spread * 0.3
        l = min(o, c) - abs(rng.normal(0.5, 0.4)) - spread * 0.3
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
        prev_close = c
    close = np.array(closes)

    volume = rng.integers(500, 5000, size=bars)

    df = pd.DataFrame({
        "datetime": dt_index,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": close,
        "volume": volume,
    })
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="تولید داده نمونه XAUUSD")
    parser.add_argument("--bars", type=int, default=3000)
    parser.add_argument("--out", default="data/sample_xauusd_h1.csv")
    args = parser.parse_args()

    data = generate(args.bars)
    data.to_csv(args.out, index=False)
    print(f"{len(data)} کندل نمونه در {args.out} ذخیره شد.")
