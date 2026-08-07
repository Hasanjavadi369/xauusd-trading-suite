"""
کانکتور دریافت داده‌ی بازار از Twelve Data API (https://twelvedata.com).

این ماژول جایگزین/مکمل MT5 برای دریافت داده‌ی تاریخی و شبه‌زنده است — به‌خصوص
مفید برای داشبورد وب (Streamlit Cloud) که روی لینوکس اجرا می‌شود و امکان اتصال
مستقیم به MetaTrader5 را ندارد.

⚠️ نکته امنیتی مهم:
کلید API هرگز نباید داخل کد یا فایل‌های commit‌شده به گیت‌هاب نوشته شود.
همیشه از متغیر محیطی `TWELVEDATA_API_KEY` یا `st.secrets["twelvedata_api_key"]`
(در Streamlit Cloud → Settings → Secrets) استفاده کنید.
"""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
import requests

BASE_URL = "https://api.twelvedata.com"

# نگاشت تایم‌فریم‌های داخلی پروژه به فرمت مورد قبول Twelve Data
INTERVAL_MAP = {
    "M1": "1min", "M5": "5min", "M15": "15min", "M30": "30min",
    "H1": "1h", "H4": "4h", "D1": "1day", "W1": "1week", "MN1": "1month",
}


class TwelveDataError(Exception):
    """خطای بازگشتی از سرور Twelve Data (کلید نامعتبر، محدودیت نرخ، نماد اشتباه و غیره)."""


def get_api_key(explicit_key: Optional[str] = None) -> str:
    """
    اولویت دریافت کلید:
    1. مقدار صریح پاس داده‌شده به تابع (مثلاً از UI کاربر)
    2. متغیر محیطی TWELVEDATA_API_KEY
    3. در صورت نبود، خطا می‌دهد (کلید هرگز hardcode نمی‌شود)
    """
    if explicit_key:
        return explicit_key
    env_key = os.environ.get("TWELVEDATA_API_KEY")
    if env_key:
        return env_key
    raise TwelveDataError(
        "کلید API یافت نشد. آن را به‌عنوان متغیر محیطی TWELVEDATA_API_KEY تنظیم کنید "
        "یا در Streamlit Secrets وارد کنید (به docs/DEPLOY.md مراجعه شود)."
    )


def fetch_time_series(symbol: str = "XAU/USD", interval: str = "H1",
                       outputsize: int = 500, api_key: Optional[str] = None,
                       timeout: int = 15) -> pd.DataFrame:
    """
    دریافت داده‌ی کندلی تاریخی از Twelve Data و تبدیل به فرمت استاندارد پروژه
    (ستون‌های time, open, high, low, close, volume — مرتب صعودی بر اساس زمان).

    symbol: فرمت Twelve Data، مثلاً "XAU/USD" برای طلا، یا "EUR/USD"، "BTC/USD" و ...
    interval: یکی از کلیدهای INTERVAL_MAP (M1..MN1) یا مستقیماً فرمت Twelve Data (مثل "1h")
    outputsize: تعداد کندل (حداکثر ۵۰۰۰ بسته به پلن حساب)
    """
    key = get_api_key(api_key)
    td_interval = INTERVAL_MAP.get(interval, interval)

    params = {
        "symbol": symbol,
        "interval": td_interval,
        "outputsize": outputsize,
        "apikey": key,
        "order": "ASC",
        "timezone": "UTC",
    }

    response = requests.get(f"{BASE_URL}/time_series", params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") == "error" or "values" not in payload:
        message = payload.get("message", "پاسخ نامعتبر از Twelve Data")
        raise TwelveDataError(f"خطای Twelve Data: {message}")

    values = payload["values"]
    df = pd.DataFrame(values)

    df = df.rename(columns={"datetime": "time"})
    numeric_cols = ["open", "high", "low", "close"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    else:
        df["volume"] = 0.0  # ابزارهایی مثل فارکس/طلا معمولاً حجم واقعی گزارش نمی‌کنند

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df[["time", "open", "high", "low", "close", "volume"]]


def fetch_latest_price(symbol: str = "XAU/USD", api_key: Optional[str] = None,
                        timeout: int = 10) -> float:
    """دریافت آخرین قیمت لحظه‌ای (Quote) — برای نمایش قیمت زنده در داشبورد."""
    key = get_api_key(api_key)
    params = {"symbol": symbol, "apikey": key}
    response = requests.get(f"{BASE_URL}/price", params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()

    if "price" not in payload:
        message = payload.get("message", "پاسخ نامعتبر از Twelve Data")
        raise TwelveDataError(f"خطای Twelve Data: {message}")

    return float(payload["price"])
