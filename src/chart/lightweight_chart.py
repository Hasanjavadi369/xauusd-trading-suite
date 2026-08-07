"""
بایندینگ پایتون برای چارت حرفه‌ای نسخه ۱ (Lightweight Charts - همان کتابخانه‌ی TradingView).

این ماژول جایگزین/تکمیل‌کننده‌ی src/chart/chart_app.py (Plotly) است و مخصوص «ساختار چارت»
طبق اسپک نسخه‌ی اول طراحی شده: نوار بالایی، ناحیه اصلی، ابزار ترسیم سمت چپ، پنل اطلاعات
سمت راست، نوار پایین. هیچ داده‌ی ساختگی در این ماژول تولید نمی‌شود — همیشه دیتافریم واقعی
(از Twelve Data API یا هر منبع آنلاین دیگر) از بیرون به آن داده می‌شود.

استفاده:
    from src.chart.lightweight_chart import render_professional_chart
    render_professional_chart(df, symbol="XAUUSD", timeframe="H1")
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

_TEMPLATE_PATH = Path(__file__).parent / "web" / "professional_chart.html"


def _df_to_candles(df: pd.DataFrame) -> list[dict]:
    """تبدیل دیتافریم OHLCV پروژه (ستون‌های time/open/high/low/close/volume) به فرمت
    مورد نیاز Lightweight Charts: زمان به‌صورت Unix timestamp (ثانیه)."""
    if "time" not in df.columns:
        raise ValueError("دیتافریم ورودی باید ستون 'time' داشته باشد.")

    out = []
    times = pd.to_datetime(df["time"])
    for i in range(len(df)):
        row = df.iloc[i]
        out.append({
            "time": int(times.iloc[i].timestamp()),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row.get("volume", 0) or 0),
        })
    return out


def build_chart_html(
    df: pd.DataFrame,
    symbol: str = "XAUUSD",
    timeframe: str = "H1",
    height: int = 720,
    connection_ok: bool = True,
) -> str:
    """
    HTML کامل و مستقل (self-contained) چارت حرفه‌ای را می‌سازد.

    df: دیتافریم OHLCV واقعی (از منبع آنلاین). هیچ داده‌ی نمونه/شبیه‌سازی‌شده‌ای اینجا
        تولید یا جایگزین نمی‌شود — اگر df خالی باشد، چارت خالی نمایش داده می‌شود.
    height: ارتفاع کلی ویجت به پیکسل.
    connection_ok: وضعیت اتصال به منبع داده‌ی زنده (برای نمایش نشانگر سبز/قرمز).
    """
    candles = _df_to_candles(df) if df is not None and len(df) else []

    html = _TEMPLATE_PATH.read_text(encoding="utf-8")
    html = html.replace("__SYMBOL__", symbol)
    html = html.replace("__TIMEFRAME__", timeframe)
    html = html.replace("__HEIGHT__", str(height))
    html = html.replace("__CONNECTION_OK__", "true" if connection_ok else "false")
    html = html.replace("__DATA_JSON__", json.dumps(candles))
    return html


def render_professional_chart(
    df: pd.DataFrame,
    symbol: str = "XAUUSD",
    timeframe: str = "H1",
    height: int = 720,
    connection_ok: bool = True,
) -> None:
    """این تابع را مستقیم داخل یک اسکریپت Streamlit صدا بزنید تا ویجت رندر شود."""
    import streamlit.components.v1 as components

    html = build_chart_html(df, symbol=symbol, timeframe=timeframe, height=height, connection_ok=connection_ok)
    components.html(html, height=height + 20, scrolling=False)
