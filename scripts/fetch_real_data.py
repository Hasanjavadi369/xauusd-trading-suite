"""
دریافت داده‌ی تاریخی **واقعی** XAUUSD از Twelve Data و ذخیره در CSV — جایگزین
داده‌ی شبیه‌سازی‌شده برای بک‌تست، آموزش مدل AI، و تحلیل CLI.

نکته: پلن رایگان Twelve Data معمولاً هر درخواست را به ۵۰۰۰ کندل محدود می‌کند و
سقف روزانه‌ی درخواست دارد؛ برای تاریخچه‌ی طولانی‌تر، اسکریپت را چند بار با
`--end-date` متفاوت اجرا کنید یا پلن حساب را ارتقا دهید.

مثال اجرا:
    export TWELVEDATA_API_KEY="کلید-شما"
    python scripts/fetch_real_data.py --symbol XAU/USD --interval H1 \
        --bars 5000 --out data/xauusd_real_h1.csv
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connectors.twelvedata_connector import fetch_time_series, TwelveDataError
from src.core.utils import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="دریافت داده تاریخی واقعی از Twelve Data")
    parser.add_argument("--symbol", default="XAU/USD")
    parser.add_argument("--interval", default="H1",
                        choices=["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"])
    parser.add_argument("--bars", type=int, default=5000, help="تعداد کندل (حداکثر بسته به پلن حساب)")
    parser.add_argument("--out", default="data/xauusd_real.csv")
    parser.add_argument("--api-key", default=None, help="در صورت عدم استفاده از متغیر محیطی")
    args = parser.parse_args()

    logger.info(f"در حال دریافت {args.bars} کندل {args.symbol} ({args.interval}) از Twelve Data...")
    try:
        df = fetch_time_series(
            symbol=args.symbol, interval=args.interval,
            outputsize=args.bars, api_key=args.api_key,
        )
    except TwelveDataError as e:
        logger.error(f"خطای Twelve Data: {e}")
        sys.exit(1)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df.to_csv(args.out, index=False)
    logger.info(f"{len(df)} کندل واقعی در {args.out} ذخیره شد "
                f"(بازه: {df['time'].iloc[0]} تا {df['time'].iloc[-1]})")


if __name__ == "__main__":
    main()
