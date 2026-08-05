# XAUUSD Trading Suite

نرم‌افزار حرفه‌ای تحلیل، بک‌تست و مدیریت معاملات برای طلا (XAUUSD) با پایتون.

**توسعه‌دهنده:** Hasan Javadi
**Telegram:** [@mr_hj369](https://t.me/mr_hj369)

## ویژگی‌ها

- اتصال به MetaTrader 5 برای دریافت داده‌های زنده و ارسال/مدیریت سفارش‌ها
- موتور تحلیل ترکیبی:
  - Smart Money Concept (SMC) / ICT: Order Blocks, Fair Value Gaps (FVG), Liquidity, BOS, CHOCH, Supply & Demand
  - Price Action: الگوهای کندلی، حمایت/مقاومت
  - اندیکاتورهای کلاسیک: EMA, SMA, RSI, MACD, ATR, VWAP, ADX, Bollinger Bands, SuperTrend, Ichimoku, Fibonacci
- پیشنهاد خودکار Entry / Stop Loss / Take Profit / Risk-Reward
- مدیریت سرمایه و ریسک: حجم معامله خودکار بر اساس درصد ریسک، Trailing Stop، Break Even، Max Drawdown
- موتور بک‌تست و بهینه‌سازی روی داده‌های تاریخی MT5 با معیارهای Win Rate، Profit Factor، Sharpe Ratio، Max Drawdown، Equity Curve
- چارت تعاملی (کندل‌استیک + همه‌ی لایه‌های تحلیلی) با Plotly/Dash
- معماری ماژولار و شی‌گرا، قابل توسعه برای استراتژی‌ها و مدل‌های هوش مصنوعی آینده

## وضعیت پروژه

این نسخه **فاز ۱ (هسته‌ی تحلیلی و بک‌تست)** است. برای جزئیات نقشه‌ی راه به `docs/ARCHITECTURE.md` مراجعه کنید.

## نصب سریع

```bash
pip install -r requirements.txt
python -m src.main --mode backtest --csv data/sample_xauusd_h1.csv
```

برای اتصال زنده به MT5 به `docs/INSTALL.md` مراجعه کنید (نیازمند ویندوز + ترمینال MetaTrader 5).

## ساختار پروژه

```
xauusd_trading_suite/
├── config/                # فایل تنظیمات (نمادها، ریسک، اندیکاتورها)
├── src/
│   ├── connectors/        # اتصال MT5 (داده و اجرای سفارش)
│   ├── indicators/        # اندیکاتورهای کلاسیک
│   ├── smc/                # Order Block, FVG, Liquidity, BOS/CHOCH
│   ├── price_action/       # کندل‌استیک، حمایت/مقاومت
│   ├── strategy/           # موتور سیگنال (ترکیب همه تحلیل‌ها)
│   ├── risk_management/    # حجم معامله، تریلینگ استاپ، بریک‌ایون
│   ├── backtest/           # موتور بک‌تست و بهینه‌سازی
│   ├── chart/              # چارت تعاملی
│   └── core/               # مدل‌های داده و ابزارهای مشترک
├── tests/                  # تست‌های واحد
└── docs/                   # مستندات
```

## لایسنس

MIT — به فایل `LICENSE` مراجعه کنید.
