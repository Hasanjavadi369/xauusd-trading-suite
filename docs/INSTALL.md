# راهنمای نصب — XAUUSD Trading Suite

## پیش‌نیازها

- Python 3.10 یا بالاتر
- برای اتصال **زنده** به MT5: ویندوز + ترمینال MetaTrader 5 نصب‌شده و یک حساب معاملاتی (دمو یا واقعی)
- برای بک‌تست و چارت روی داده تاریخی: هیچ نیاز به ویندوز یا MT5 نیست (روی لینوکس/مک هم کار می‌کند)

## نصب

```bash
git clone https://github.com/<your-username>/xauusd-trading-suite.git
cd xauusd-trading-suite
python -m venv .venv
source .venv/bin/activate        # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
```

برای اتصال زنده به MT5 (فقط ویندوز)، این خط را هم در `requirements.txt` از حالت کامنت خارج و نصب کنید:

```bash
pip install MetaTrader5
```

## تست سریع (بدون MT5)

یک فایل CSV نمونه (شبیه‌سازی‌شده) از قبل در `data/sample_xauusd_h1.csv` موجود است.
برای تولید دوباره یا با تعداد کندل دلخواه:

```bash
python scripts/generate_sample_data.py --bars 3000 --out data/sample_xauusd_h1.csv
```

### اجرای بک‌تست

```bash
python -m src.main --mode backtest --csv data/sample_xauusd_h1.csv
```

### اجرای چارت تعاملی (در مرورگر باز می‌شود)

```bash
python -m src.main --mode chart --csv data/sample_xauusd_h1.csv
```

## اتصال زنده به MT5

1. ترمینال MetaTrader 5 را باز و وارد حساب خود شوید (یا اطلاعات ورود را در `config/config.yaml` زیر کلید `mt5` وارد کنید).
2. اطمینان حاصل کنید نماد `XAUUSD` (یا نام معادل آن نزد بروکر شما، مثلاً `XAUUSD.m`) در Market Watch فعال است؛ در صورت تفاوت نام، مقدار `symbol` در `config.yaml` را ویرایش کنید.
3. اجرا:

```bash
python -m src.main --mode live --send-orders False
```

`--send-orders False` فقط سیگنال را نمایش می‌دهد و معامله‌ای باز نمی‌کند. برای ارسال واقعی سفارش:

```bash
python -m src.main --mode live --send-orders True
```

⚠️ ابتدا حتماً روی حساب **دمو** تست کنید.

## اجرای تست‌های واحد

```bash
pip install pytest
pytest tests/ -v
```

## عیب‌یابی رایج

| مشکل | راه‌حل |
|---|---|
| `ModuleNotFoundError: MetaTrader5` | فقط روی ویندوز نصب می‌شود؛ در لینوکس/مک از حالت backtest/chart استفاده کنید |
| اتصال MT5 ناموفق است | مطمئن شوید ترمینال MT5 باز و لاگین است؛ `terminal_path` را در config بررسی کنید |
| نماد پیدا نشد | نام دقیق نماد نزد بروکر خود را در Market Watch بررسی و در config جایگزین کنید |
| چارت باز نمی‌شود | مطمئن شوید `dash` و `plotly` نصب شده‌اند؛ پورت پیش‌فرض Dash (8050) آزاد باشد |
