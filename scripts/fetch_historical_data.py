"""
دانلود داده‌ی تاریخی واقعی از Twelve Data و ذخیره به‌صورت CSV — برای استفاده در
آموزش مدل AI (`scripts/train_signal_model.py`).

چرا این اسکریپت لازم است؟
موتور سیگنال هرگز امتیاز AI جعلی نمی‌سازد: لایه‌ی AI فقط وقتی فعال می‌شود که یک
مدل واقعی، روی داده‌ی واقعی، از قبل train شده باشد. برای train معنادار به چند
سال کندل نیاز است (خروجی هر درخواست Twelve Data حداکثر ۵۰۰۰ کندل است)، پس این
اسکریپت با صفحه‌بندی (pagination) به‌عقب، چند سال داده را جمع می‌کند.

مثال اجرا (طلا، تایم‌فریم H1، ۳ سال گذشته):
    python -m scripts.fetch_historical_data --symbol XAU/USD --interval H1 \
        --years 3 --output data/XAUUSD_H1_real.csv

مثال برای بیت‌کوین:
    python -m scripts.fetch_historical_data --symbol BTC/USD --interval H1 \
        --years 3 --output data/BTCUSD_H1_real.csv

سپس مدل را train کنید:
    python -m scripts.train_signal_model --csv data/XAUUSD_H1_real.csv \
        --output models/signal_scorer_ensemble_xauusd.joblib
    python -m scripts.train_signal_model --csv data/BTCUSD_H1_real.csv \
        --output models/signal_scorer_ensemble_btcusd.joblib

نکته: کلید API باید به‌صورت متغیر محیطی TWELVEDATA_API_KEY در دسترس باشد.
نکته: این اسکریپت را روی سیستم خودتان اجرا کنید (نه در خودِ داشبورد وب) چون
دانلود چند سال داده ممکن است چند دقیقه طول بکشد و به سقف نرخ API حساس است.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd

from src.connectors.twelvedata_connector import fetch_time_series, TwelveDataError, INTERVAL_MAP

# میانگین تقریبی فاصله‌ی زمانی بین دو کندل، برای محاسبه‌ی گام صفحه‌بندی به‌عقب.
_INTERVAL_MINUTES = {
    "M1": 1, "M5": 5, "M15": 15, "M30": 30,
    "H1": 60, "H4": 240, "D1": 1440,
}


def main():
    parser = argparse.ArgumentParser(description="دانلود داده‌ی تاریخی واقعی از Twelve Data برای آموزش مدل")
    parser.add_argument("--symbol", default="XAU/USD", help='مثلاً "XAU/USD" یا "BTC/USD"')
    parser.add_argument("--interval", default="H1", choices=list(INTERVAL_MAP.keys()))
    parser.add_argument("--years", type=float, default=3.0, help="تعداد سال گذشته برای دانلود")
    parser.add_argument("--output", required=True, help="مسیر فایل CSV خروجی")
    parser.add_argument("--page-size", type=int, default=5000, help="حداکثر کندل هر درخواست (سقف پلن شما را رعایت کنید)")
    parser.add_argument("--sleep-seconds", type=float, default=8.0, help="فاصله بین درخواست‌های پیاپی برای رعایت سقف نرخ")
    args = parser.parse_args()

    if args.interval not in _INTERVAL_MINUTES:
        raise SystemExit(f"تایم‌فریم {args.interval} برای این اسکریپت پشتیبانی نمی‌شود.")

    target_start = datetime.now(timezone.utc) - timedelta(days=args.years * 365)
    cursor_end = None  # None یعنی از "الان" شروع کن
    all_frames: list[pd.DataFrame] = []
    page = 0

    print(f"شروع دانلود {args.symbol} [{args.interval}] از الان تا {target_start.date()} ...")
    while True:
        page += 1
        try:
            df = fetch_time_series(
                args.symbol, args.interval, args.page_size,
                end_date=cursor_end,
            )
        except TwelveDataError as exc:
            print(f"  متوقف شد در صفحه {page}: {exc}")
            break

        if df.empty:
            print("  داده‌ی بیشتری برنگشت — پایان.")
            break

        all_frames.append(df)
        earliest = df["time"].min()
        latest = df["time"].max()
        print(f"  صفحه {page}: {len(df)} کندل ({earliest} .. {latest})")

        if earliest <= pd.Timestamp(target_start):
            print("  به بازه‌ی زمانی هدف رسیدیم — پایان.")
            break

        # برای صفحه‌ی بعد، یک کندل قبل از قدیمی‌ترین کندل فعلی را به‌عنوان انتهای بازه قرار می‌دهیم.
        step = timedelta(minutes=_INTERVAL_MINUTES[args.interval])
        cursor_end = (earliest - step).strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(args.sleep_seconds)

    if not all_frames:
        raise SystemExit("هیچ داده‌ای دانلود نشد.")

    full = pd.concat(all_frames, ignore_index=True)
    full = full.drop_duplicates(subset="time").sort_values("time").reset_index(drop=True)
    full = full[full["time"] >= pd.Timestamp(target_start)].reset_index(drop=True)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    full = full.rename(columns={"time": "datetime"})
    full.to_csv(out_path, index=False)
    print(f"\n✅ {len(full)} کندل واقعی ذخیره شد در: {out_path}")
    print(f"   بازه: {full['datetime'].min()} .. {full['datetime'].max()}")
    print("\nمرحله‌ی بعد — آموزش مدل:")
    print(f"   python -m scripts.train_signal_model --csv {out_path} \\")
    print(f"       --output models/signal_scorer_ensemble_{args.symbol.replace('/', '').lower()}.joblib")


if __name__ == "__main__":
    main()
