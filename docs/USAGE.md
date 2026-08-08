# راهنمای استفاده — XAUUSD Trading Suite

## ۱. بک‌تست یک استراتژی

```bash
python -m src.main --mode backtest --csv data/XAUUSD_H1_real.csv
```

خروجی شامل: تعداد معاملات، Win Rate، Profit Factor، Sharpe Ratio، Max Drawdown، سود/زیان خالص.

### تنظیم پارامترهای ریسک و SMC

همه‌ی پارامترها در `config/config.yaml` قابل تغییرند، از جمله:

```yaml
risk:
  risk_per_trade_pct: 1.0
  reward_risk_ratio: 2.0
smc:
  swing_lookback: 5
  order_block_lookback: 20
  fvg_min_gap_pct: 0.02
```

اگر تعداد سیگنال‌ها روی داده‌ی شما کم است، `order_block_lookback` را افزایش، یا
`fvg_min_gap_pct` را کاهش دهید تا موتور حساس‌تر شود (به قیمت کاهش کیفیت فیلتر).

## ۲. بهینه‌سازی پارامترها (Grid Search)

از `src.backtest.engine.grid_search` برای جستجوی بهترین ترکیب پارامترها استفاده کنید:

```python
from src.backtest.engine import grid_search, BacktestConfig
from src.strategy.signal_engine import SMCConfluenceStrategy

def strategy_factory(swing_lookback, rr_target):
    cfg = base_config.copy()
    cfg["smc"]["swing_lookback"] = swing_lookback
    cfg["risk"]["reward_risk_ratio"] = rr_target
    strategy = SMCConfluenceStrategy(cfg)
    strategy.prepare(df)
    return lambda window: strategy.generate_latest_signal(window)

results = grid_search(
    df, strategy_factory,
    param_grid={"swing_lookback": [3, 5, 7], "rr_target": [1.5, 2.0, 3.0]},
    atr_series=df["atr"],
)
print(results.head())
```

## ۳. چارت تعاملی

```bash
python -m src.main --mode chart --csv data/XAUUSD_H1_real.csv
```

مرورگر را روی `http://127.0.0.1:8050` باز کنید. چارت شامل کندل‌استیک، حجم،
اندیکاتورهای همپوشان (EMA/Bollinger)، پنل‌های RSI/MACD، نواحی Order Block/FVG،
و خطوط Entry/SL/TP آخرین سیگنال است.

## ۴. اجرای زنده با MT5 (فقط ویندوز)

```bash
python -m src.main --mode live --send-orders False   # فقط نمایش سیگنال
python -m src.main --mode live --send-orders True    # ارسال واقعی معامله
```

اطلاعات ورود حساب را از قبل در `config/config.yaml` بخش `mt5` وارد کنید.

## ۵. مدل امتیازدهی سیگنال (Machine Learning)

علاوه بر امتیاز اطمینان قانون‌محور (`confidence`)، می‌توانید یک مدل طبقه‌بندی
(XGBoost/LightGBM/یا جایگزین سبک scikit-learn) train کنید که یاد می‌گیرد از
روی همان فیچرهای موتور SMC (فاصله/قدرت Order Block، همپوشانی و قدرت FVG،
هم‌جهتی چند اندیکاتور، ...) چه ترکیبی تاریخاً بیشتر به Take Profit رسیده تا
Stop Loss. **این مدل قیمت را پیش‌بینی نمی‌کند** — فقط سیگنال‌های قانون‌محور
موجود را امتیازدهی می‌کند و کاملاً قابل train روی داده‌ی خودتان و تفسیرپذیر
(با گزارش اهمیت فیچرها) است.

### ۵.۱ آموزش مدل روی داده‌ی زنده‌ی Twelve Data (برای داشبورد وب)

اگر می‌خواهید در داشبورد وب (`streamlit_app.py`) لایه‌ی AI برای طلا/بیت‌کوین
فعال شود، اول باید چند سال داده‌ی واقعی دانلود کنید (چون هر درخواست Twelve
Data حداکثر ۵۰۰۰ کندل برمی‌گرداند)، سپس مدل را روی همان داده train کنید.
این کار را روی سیستم خودتان اجرا کنید (نه داخل خود داشبورد وب) چون دانلود چند
سال داده چند دقیقه طول می‌کشد و باید سقف نرخ API رعایت شود:

```bash
# ۱) دانلود ۳ سال کندل واقعی H1 طلا
python -m scripts.fetch_historical_data --symbol XAU/USD --interval H1 \
    --years 3 --output data/XAUUSD_H1_real.csv

# ۲) آموزش مدل مخصوص طلا
python -m scripts.train_signal_model --csv data/XAUUSD_H1_real.csv \
    --output models/signal_scorer_ensemble_xauusd.joblib

# همین دو مرحله را برای بیت‌کوین هم تکرار کنید
python -m scripts.fetch_historical_data --symbol BTC/USD --interval H1 \
    --years 3 --output data/BTCUSD_H1_real.csv
python -m scripts.train_signal_model --csv data/BTCUSD_H1_real.csv \
    --output models/signal_scorer_ensemble_btcusd.joblib
```

نام‌گذاری فایل خروجی مهم است: موتور سیگنال زنده به‌صورت خودکار دنبال
`models/signal_scorer_ensemble_<symbol>.joblib` می‌گردد (مثلاً `..._xauusd.joblib`
یا `..._btcusd.joblib`) و اگر پیدا شود، همان مدل مخصوص همان نماد را بارگذاری
می‌کند. بعد از این مرحله، این دو فایل را همراه ریپازیتوری commit/push کنید تا
در دیپلوی Streamlit Cloud هم در دسترس باشند — و لایه‌ی AI در داشبورد به‌صورت
خودکار «ACTIVE» می‌شود.

> ⚠️ با داده‌ی کم (کمتر از چند صد سیگنال برچسب‌خورده) مدل قابل‌اعتماد نیست.
> اسکریپت `train_signal_model.py` تعداد سیگنال‌های برچسب‌خورده را گزارش
> می‌کند — اگر خیلی کم بود، بازه‌ی `--years` را افزایش دهید.

### ۵.۲ آموزش مدل از روی CSV دلخواه

```bash
python scripts/train_signal_model.py --csv data/XAUUSD_H1_real.csv
```

خروجی شامل تعداد سیگنال‌های برچسب‌خورده (برد/باخت)، معیارهای ارزیابی
(accuracy/precision/recall/F1/ROC-AUC/confusion matrix) روی یک برش **زمانی**
از داده (نه تصادفی، تا نشتِ اطلاعات از آینده رخ ندهد)، و مقایسه با baseline
قانون‌محور خام. مدل در `models/signal_scorer.joblib` و متادیتای آموزش در
`models/signal_scorer.meta.json` ذخیره می‌شود.

گزینه‌های مهم:

```bash
python scripts/train_signal_model.py \
    --csv data/my_5years_h1.csv \
    --backend xgboost \
    --output models/signal_scorer.joblib \
    --test-size 0.25 \
    --max-horizon-bars 200
```

> نکته: با داده‌ی نمونه‌ی کوچک پروژه فقط چند ده سیگنال برچسب‌خورده به دست
> می‌آید که برای نمایش/تست کافی است اما برای یک مدل قابل‌اعتماد واقعی به
> چند سال داده‌ی تاریخی (چند صد سیگنال) نیاز دارید.

### ۵.۲ فعال‌سازی مدل در بک‌تست/زنده

در `config/config.yaml`:

```yaml
ml:
  enabled: true
  model_path: "models/signal_scorer.joblib"
  min_probability: 0.0   # اگر > 0، سیگنال‌های زیر این احتمال نادیده گرفته می‌شوند
```

با `ml.enabled: true`، همان دستورات بک‌تست/زنده‌ی بالا خودکار مدل را بارگذاری
می‌کنند و هر سیگنال یک فیلد `ml_probability` و یک دلیل اضافه در `reasons`
می‌گیرد. اگر فایل مدل پیدا نشود یا مدل train نشده باشد، اجرای برنامه متوقف
نمی‌شود — فقط هشدار می‌دهد و مثل قبل بدون امتیاز ML ادامه می‌دهد.

### ۵.۳ استفاده مستقیم در کد

```python
from src.ml.scorer import SignalScorer
from src.strategy.signal_engine import SMCConfluenceStrategy

scorer = SignalScorer.load("models/signal_scorer.joblib")
strategy = SMCConfluenceStrategy(config, scorer=scorer)
df = strategy.prepare(df)

signal = strategy.generate_latest_signal(df)
if signal:
    print(signal.confidence, signal.ml_probability)  # قانون‌محور و ML کنار هم
```

در داشبورد Streamlit هم بخش «🤖 مدل امتیازدهی سیگنال (ML)» در نوار کناری
اضافه شده که مسیر مدل، فعال‌سازی، و آستانه‌ی حداقل احتمال را تنظیم می‌کند.

## ۶. استفاده مستقیم از ماژول‌ها در کد خودتان

```python
import pandas as pd
from src.core.utils import load_config
from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy

config = load_config("config/config.yaml")
df = pd.read_csv("data/XAUUSD_H1_real.csv", parse_dates=["datetime"])
df = df.rename(columns={"datetime": "time"})

df = compute_all_indicators(df, config)
strategy = SMCConfluenceStrategy(config)
df = strategy.prepare(df)

signal = strategy.generate_latest_signal(df)
if signal:
    print(signal.direction, signal.entry_price, signal.stop_loss,
          signal.take_profit, signal.risk_reward, signal.confidence)
    for reason in signal.reasons:
        print("-", reason)
```

## سلب مسئولیت

این نرم‌افزار صرفاً ابزار تحلیلی/آموزشی است و **توصیه مالی محسوب نمی‌شود**.
معاملات فارکس/طلا با اهرم دارای ریسک از دست دادن سرمایه است. قبل از استفاده
با حساب واقعی، حتماً روی حساب دمو تست و استراتژی را بر اساس تحمل ریسک خود
تنظیم کنید.
