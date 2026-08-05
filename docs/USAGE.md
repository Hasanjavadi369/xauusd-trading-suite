# راهنمای استفاده — XAUUSD Trading Suite

## ۱. بک‌تست یک استراتژی

```bash
python -m src.main --mode backtest --csv data/sample_xauusd_h1.csv
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
python -m src.main --mode chart --csv data/sample_xauusd_h1.csv
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

## ۵. استفاده مستقیم از ماژول‌ها در کد خودتان

```python
import pandas as pd
from src.core.utils import load_config
from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy

config = load_config("config/config.yaml")
df = pd.read_csv("data/sample_xauusd_h1.csv", parse_dates=["datetime"])
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
