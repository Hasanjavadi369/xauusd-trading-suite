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

این پروژه هیچ داده‌ی فرضی/شبیه‌سازی‌شده‌ای همراه ندارد. برای اجرا باید یک منبع
داده‌ی **واقعی** فراهم کنید — یکی از این دو راه:

1. **فایل CSV واقعی خودتان**: خروجی تاریخچه‌ی قیمت از MT5 (Export to CSV)،
   بروکر، یا هر منبع معتبر دیگر، با ستون‌های
   `datetime, open, high, low, close, volume` و ذخیره در مسیر دلخواه
   (مثلاً `data/XAUUSD_H1_real.csv`).
2. **Twelve Data API**: با گرفتن یک کلید رایگان از
   [twelvedata.com](https://twelvedata.com) و تنظیم آن به‌صورت متغیر محیطی
   `TWELVEDATA_API_KEY`، داده‌ی واقعی زنده مستقیماً در داشبورد Streamlit یا
   از طریق `src/connectors/twelvedata_connector.py` دریافت می‌شود.

### اجرای بک‌تست

```bash
python -m src.main --mode backtest --csv data/XAUUSD_H1_real.csv
```

### اجرای چارت تعاملی (در مرورگر باز می‌شود)

```bash
python -m src.main --mode chart --csv data/XAUUSD_H1_real.csv
```

## اتصال به Twelve Data API (داده زنده، جایگزین سبک MT5)

برای دریافت داده از [Twelve Data](https://twelvedata.com) (کار می‌کند روی هر سیستم‌عاملی،
از جمله سرورهای ابری لینوکسی که MT5 روی آن‌ها اجرا نمی‌شود):

1. یک حساب رایگان در twelvedata.com بسازید و کلید API را از داشبورد کپی کنید
2. کلید را **در کد قرار ندهید** — به‌جای آن:
   ```bash
   export TWELVEDATA_API_KEY="کلید-شما"      # لینوکس/مک
   set TWELVEDATA_API_KEY=کلید-شما           # ویندوز (cmd)
   ```
3. اجرای داشبورد:
   ```bash
   streamlit run streamlit_app.py
   ```
   و از نوار کناری «Twelve Data API (زنده)» را انتخاب کنید.

برای دیپلوی روی Streamlit Cloud، کلید را در پنل **Secrets** وارد کنید (نه در فایل)؛
جزئیات کامل در `docs/DEPLOY.md`.

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
