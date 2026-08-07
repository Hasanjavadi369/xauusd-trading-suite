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
- **لایه یادگیری ماشین** که مستقیماً از رفتار تاریخی قیمت یاد می‌گیرد (بدون تکیه به قوانین
  از پیش تعریف‌شده)، و قابل ترکیب با موتور SMC در یک «موتور ادغامی» — جزئیات: `docs/AI_MODEL.md`
- پیشنهاد خودکار Entry / Stop Loss / Take Profit / Risk-Reward
- مدیریت سرمایه و ریسک: حجم معامله خودکار بر اساس درصد ریسک، Trailing Stop، Break Even، Max Drawdown
- موتور بک‌تست و بهینه‌سازی روی داده‌های تاریخی MT5 با معیارهای Win Rate، Profit Factor، Sharpe Ratio، Max Drawdown، Equity Curve
- چارت تعاملی (کندل‌استیک + همه‌ی لایه‌های تحلیلی) با Plotly/Dash
- معماری ماژولار و شی‌گرا، قابل توسعه برای استراتژی‌ها و مدل‌های هوش مصنوعی آینده

## وضعیت پروژه

این نسخه **فاز ۱ (هسته‌ی تحلیلی و بک‌تست)** است. برای جزئیات نقشه‌ی راه به `docs/ARCHITECTURE.md` مراجعه کنید.

## 🌐 داشبورد وب زنده (لینک عمومی از طریق گیت‌هاب)

این پروژه یک داشبورد Streamlit (`streamlit_app.py`) دارد که با اتصال ریپازیتوری
به [Streamlit Community Cloud](https://share.streamlit.io) به یک **لینک عمومی
همیشه در دسترس** تبدیل می‌شود — با باز کردن لینک (حتی از گوشی)، داشبورد خودش
اجرا می‌شود، بدون نیاز به نصب چیزی. راهنمای کامل: `docs/DEPLOY.md`

اجرای محلی داشبورد:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## نصب سریع (CLI)

```bash
pip install -r requirements.txt

# دریافت داده تاریخی واقعی (نیازمند کلید رایگان Twelve Data)
export TWELVEDATA_API_KEY="کلید-شما"
python scripts/fetch_real_data.py --symbol XAU/USD --interval H1 --bars 5000 --out data/xauusd_real.csv

python -m src.main --mode backtest --csv data/xauusd_real.csv
```

⚠️ این پروژه از داده‌ی شبیه‌سازی‌شده استفاده نمی‌کند — تحلیل/بک‌تست/آموزش مدل فقط
روی داده‌ی واقعی (Twelve Data یا خروجی MT5) انجام می‌شود.

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
