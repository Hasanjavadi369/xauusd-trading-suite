# معماری پروژه — XAUUSD Trading Suite

## دیدگاه کلی

```
داده (CSV یا MT5) → اندیکاتورها → موتور SMC/ICT → موتور سیگنال (Confluence)
        → [ مدیریت ریسک/حجم ] → [ بک‌تست  یا  اجرای زنده MT5 ] → گزارش/چارت
```

## ماژول‌ها

### `src/core`
- `data_models.py`: ساختارهای داده مشترک (`Signal`, `Trade`, `Zone`, `MarketStructurePoint`).
  تمام ماژول‌های دیگر از همین مدل‌ها استفاده می‌کنند تا داده‌ها بین بخش‌ها سازگار بماند.
- `utils.py`: بارگذاری config، اعتبارسنجی دیتافریم OHLC.

### `src/indicators`
هر فایل یک دسته اندیکاتور را پیاده‌سازی می‌کند (trend, momentum, volatility, volume, fibonacci).
`calculator.py` همه را طبق `config.yaml` روی یک دیتافریم اجرا و ادغام می‌کند.

### `src/smc`
پیاده‌سازی مفاهیم Smart Money Concept / ICT:
- `structure.py`: Swing High/Low، BOS، CHOCH
- `order_blocks.py`: شناسایی و ردیابی mitigation آردر بلاک‌ها
- `fvg.py`: شکاف‌های قیمتی (Fair Value Gap)
- `liquidity.py`: Equal Highs/Lows و شکار نقدینگی
- `supply_demand.py`: نواحی عرضه/تقاضا بر پایه الگوی base + impulse

### `src/price_action`
- `candlestick_patterns.py`: Pin Bar، Engulfing، Doji، Morning/Evening Star
- `support_resistance.py`: خوشه‌بندی نقاط سوینگ برای یافتن سطوح معتبر

### `src/strategy`
- `base_strategy.py`: کلاس پایه انتزاعی — هر استراتژی/مدل AI آینده از این ارث‌بری می‌کند.
- `signal_engine.py` (`SMCConfluenceStrategy`): موتور اصلی که خروجی همه‌ی ماژول‌های بالا
  را ترکیب کرده و امتیاز اطمینان (confidence) + Entry/SL/TP/RR تولید می‌کند.

### `src/ml`
مدل امتیازدهی سیگنال (Signal Scoring Model) — **نه پیش‌بینی قیمت**:
- `features.py`: اسکیمای مشترک فیچرها (تنها منبع حقیقت برای نام/ترتیب ستون‌ها،
  هم در آموزش هم در inference، تا هیچ train/serve skew رخ ندهد).
- `dataset.py`: ساخت دیتاست برچسب‌خورده با replay walk-forward دقیقاً هم‌ترازِ
  نحوه‌ی مصرف واقعی سیگنال در `backtest/engine.py` (هر سیگنال از لحظه‌ی تشخیص
  دنبال می‌شود تا مشخص شود TP زودتر لمس شد یا SL).
- `scorer.py` (`SignalScorer`): کلاس train/predict/save/load با بک‌اند
  XGBoost → LightGBM → `HistGradientBoostingClassifier` (سقوط sklearn، همیشه
  در دسترس)، به‌همراه گزارش اهمیت فیچرها برای تفسیرپذیری.
- `scripts/train_signal_model.py`: CLI آموزش با تقسیم زمانی train/test و گزارش
  کامل معیارها.

`SMCConfluenceStrategy` می‌تواند یک `SignalScorer` اختیاری بگیرد؛ اگر داده شود،
هر `Signal` علاوه بر `confidence` قانون‌محور، یک `ml_probability` هم می‌گیرد.
بدون آن، رفتار موتور دقیقاً مثل قبل (فقط قانون‌محور) است.

### `src/risk_management`
- `position_sizing.py`: محاسبه حجم لات بر اساس درصد ریسک.
- `trade_manager.py`: Break Even، Trailing Stop، و آستانه‌های توقف روزانه/Max Drawdown.

### `src/backtest`
- `engine.py`: شبیه‌سازی bar-by-bar معاملات + `grid_search` برای بهینه‌سازی پارامترها.
- `metrics.py`: Win Rate، Profit Factor، Sharpe Ratio، Max Drawdown، Equity Curve.

### `src/chart`
- `chart_app.py`: چارت کندل‌استیک تعاملی (Plotly/Dash) با لایه‌های SMC، اندیکاتورها،
  و نشانگر Entry/SL/TP — قابل اجرا مستقل یا از طریق `main.py`.

### `streamlit_app.py` (ریشه پروژه)
داشبورد وب مبتنی بر Streamlit که همان `build_figure` از `chart_app.py` را برای
رسم چارت استفاده می‌کند، به‌علاوه پنل تنظیمات ریسک/SMC و اجرای بک‌تست از طریق UI.
برای دیپلوی رایگان با لینک عمومی روی Streamlit Community Cloud طراحی شده
(`docs/DEPLOY.md`).

### `src/connectors`
- `mt5_connector.py`: پوشش کامل روی پکیج `MetaTrader5` برای داده و اجرای سفارش
  (فقط روی ویندوز فعال است؛ در سایر سیستم‌عامل‌ها gracefully غیرفعال می‌شود).

## افزودن استراتژی یا اندیکاتور جدید

1. **اندیکاتور جدید**: تابعی در `src/indicators/<file>.py` اضافه کنید و آن را در
   `calculator.compute_all_indicators` فراخوانی کنید.
2. **استراتژی جدید**: کلاسی از `BaseStrategy` بسازید و `prepare()` / `generate_signals()`
   را پیاده‌سازی کنید؛ خروجی باید لیستی از `Signal` باشد تا با بک‌تست/اجرای زنده سازگار بماند.
3. **مدل هوش مصنوعی آینده**: `src/ml` دقیقاً همین الگو را برای امتیازدهی سیگنال
   (نه پیش‌بینی قیمت) پیاده کرده — ویژگی‌های محاسبه‌شده توسط `indicators` و `smc`
   به‌عنوان ورودی یک classifier استفاده می‌شوند؛ برای مدل‌های AI بعدی (مثلاً
   regression روی اندازه‌ی حرکت، یا یک استراتژی کاملاً یادگیری‌محور) همین الگوی
   جداسازی «فیچر مشترک ↔ مدل قابل‌جایگزین» قابل استفاده مجدد است.

## محدودیت‌های شناخته‌شده (نسخه فعلی)

- موتور بک‌تست هر بار فقط **یک معامله باز** را مدیریت می‌کند (ساده‌سازی‌شده)؛ برای چند
  معامله همزمان باید `BacktestEngine` گسترش یابد.
- استراتژی SMC پیش‌فرض عمداً محافظه‌کار است (فقط آردر بلاک‌های تازه/mitigate‌نشده و
  هم‌جهت با ساختار بازار)؛ روی داده‌های نویزی/رنج تعداد سیگنال کم خواهد بود — از طریق
  `config.yaml` (`smc.*`, `risk.reward_risk_ratio`) قابل تنظیم است.
- چارت فعلی یک وب‌اپ Dash محلی است، نه یک ابزار گرافیکی مستقل مانند دسکتاپ TradingView؛
  برای نسخه دسکتاپ می‌توان همین `build_figure` را در یک اپ PyQt/PySide با `QWebEngineView` جای داد.
