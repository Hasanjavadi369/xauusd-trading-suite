# Focused Live Signal Engine — Gold + Bitcoin

The dashboard covers two instruments from the same page: **live XAU/USD (Gold)**
and **live BTC/USD (Bitcoin)** signal generation, selectable with a switch at
the top of the dashboard. Both share the same Twelve Data API key and the same
pipeline. It uses real M5/M15/H1/H4/D1 market data and follows:

`Live Price → MTF → Structure → Liquidity/SMC/ICT → Technical/Candles → Volatility/Momentum → AI Confirmation → Score → BUY/SELL/NO TRADE → Entry/SL/TP`

No synthetic market prices are generated. The AI layer is activated only when a trained real-data ensemble model is present.

### کلید API

کلید Twelve Data دیگر در داشبورد وارد نمی‌شود؛ به‌صورت خودکار و بی‌صدا از
**Streamlit Secrets** خوانده می‌شود. قبل از اجرا، در فایل `.streamlit/secrets.toml`
(یا در Streamlit Cloud → Settings → Secrets) این را اضافه کنید:

```toml
TWELVEDATA_API_KEY = "کلید_شما_اینجا"
```

اگر کلید تنظیم نشده باشد، داشبورد پیام خطای واضح می‌دهد و از اجرای تحلیل با
داده‌ی جعلی/بدون کلید خودداری می‌کند.

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
- 🆕 **مدل امتیازدهی سیگنال (Machine Learning)**: یک classifier (XGBoost/LightGBM)
  که از همان فیچرهای موتور SMC (فاصله/قدرت Order Block، قدرت FVG، هم‌جهتی چند
  اندیکاتور) یاد می‌گیرد احتمال موفقیت هر سیگنال چقدر است — تفسیرپذیر و کاملاً
  قابل train روی داده‌ی خودتان (نه جعبه‌سیاه، و نه پیش‌بینی قیمت). جزئیات: بخش
  «۵. مدل امتیازدهی سیگنال» در `docs/USAGE.md`.
- معماری ماژولار و شی‌گرا، قابل توسعه برای استراتژی‌ها و مدل‌های هوش مصنوعی آینده

## 🆕 ارتقاهای این نسخه

- داشبورد Streamlit با طراحی تازه: هدر با قیمت لحظه‌ای و درصد تغییر، کارت‌های
  خلاصه بازار، کارت سیگنال رنگی (خرید/فروش)، و چیدمان سه‌تبی (تحلیل زنده /
  بک‌تست حرفه‌ای / راهنما).
- کنترل نمایش لایه‌های چارت (Order Block، FVG، Supply/Demand، نقدینگی،
  حمایت/مقاومت) به‌صورت جداگانه از نوار کناری.
- تب بک‌تست با Equity Curve + Drawdown، جدول کامل معاملات و دانلود CSV.
- این پروژه هیچ داده‌ی فرضی/شبیه‌سازی‌شده‌ای همراه ندارد؛ تمام تحلیل‌ها فقط
  روی داده‌ی واقعی (CSV واقعی شما یا Twelve Data API زنده) اجرا می‌شوند.

## وضعیت پروژه

این نسخه **فاز ۱ (هسته‌ی تحلیلی و بک‌تست)** است. برای جزئیات نقشه‌ی راه به `docs/ARCHITECTURE.md` مراجعه کنید.

## 🌐 داشبورد وب زنده (لینک عمومی از طریق گیت‌هاب)

این پروژه یک داشبورد Streamlit (`streamlit_app.py`) دارد که با اتصال ریپازیتوری
به [Streamlit Community Cloud](https://share.streamlit.io) به یک **لینک عمومی
همیشه در دسترس** تبدیل می‌شود — با باز کردن لینک (حتی از گوشی)، داشبورد خودش
اجرا می‌شود، بدون نیاز به نصب چیزی. کلید API را در Streamlit Secrets تنظیم کنید
(بالاتر توضیح داده شد) — چیزی در خود صفحه وارد نمی‌کنید. راهنمای کامل: `docs/DEPLOY.md`

اجرای محلی داشبورد:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## نصب سریع (CLI)

```bash
pip install -r requirements.txt
python -m src.main --mode backtest --csv data/XAUUSD_H1_real.csv
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
│   ├── ml/                 # مدل امتیازدهی سیگنال (train/predict، نه پیش‌بینی قیمت)
│   ├── chart/              # چارت تعاملی
│   └── core/               # مدل‌های داده و ابزارهای مشترک
├── scripts/
│   └── train_signal_model.py  # آموزش مدل امتیازدهی سیگنال (روی CSV واقعی)
├── models/                 # مدل‌های train‌شده (.joblib) + متادیتا (.meta.json)
├── tests/                  # تست‌های واحد
└── docs/                   # مستندات
```

## لایسنس

MIT — به فایل `LICENSE` مراجعه کنید.
