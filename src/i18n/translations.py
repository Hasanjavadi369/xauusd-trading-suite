# -*- coding: utf-8 -*-
"""دیکشنری کامل ترجمه‌های داشبورد (فارسی / انگلیسی)."""

TRANSLATIONS = {
    "fa": {
        # --- عمومی ---
        "app_title": "📈 XAUUSD Trading Suite",
        "app_subtitle": "داشبورد تحلیل زنده · SMC/ICT + اندیکاتورهای کلاسیک · Hasan Javadi · Telegram: @mr_hj369",
        "footer_text": "⚠️ این نرم‌افزار صرفاً ابزار تحلیلی/آموزشی است و توصیه مالی محسوب نمی‌شود. "
                        "معاملات حساب دمو کاملاً شبیه‌سازی‌شده و بدون پول واقعی است. "
                        "اتصال زنده به MT5 روی این داشبورد ابری فعال نیست (فقط ویندوز).",

        # --- نوار کناری: عمومی ---
        "sidebar_title": "⚙️ تنظیمات",
        "lang_switch_label": "🌐 زبان",

        "data_source_header": "📥 منبع داده (فقط آنلاین/واقعی)",
        "data_source_radio_label": "داده از کجا بیاید؟",
        "data_source_option_live": "Twelve Data API (زنده)",
        "data_source_option_csv": "آپلود CSV",
        "csv_uploader_label": "فایل CSV",
        "td_symbol_label": "نماد (فرمت Twelve Data)",
        "td_timeframe_label": "تایم‌فریم",
        "td_fetch_btn": "📡 دریافت داده از Twelve Data",
        "auto_refresh_checkbox": "🔄 به‌روزرسانی خودکار (چارت زنده)",
        "auto_refresh_interval_label": "فاصله‌ی به‌روزرسانی (ثانیه)",
        "live_status_live": "🟢 زنده — آخرین به‌روزرسانی: {ts}",
        "live_status_stale": "🟡 آخرین داده (بدون اتصال زنده): {ts}",
        "api_key_guide_expander": "راهنمای کلید API",
        "api_key_guide_text": (
            "کلید API را در این کد وارد نکنید. آن را در Streamlit Cloud → "
            "**Settings → Secrets** با نام `twelvedata_api_key` ثبت کنید، یا هنگام اجرای "
            "محلی متغیر محیطی `TWELVEDATA_API_KEY` را تنظیم کنید. جزئیات: docs/DEPLOY.md"
        ),
        "csv_loaded_success": "{n} کندل از فایل شما بارگذاری شد.",
        "td_fetched_success": "{n} کندل دریافت شد.",
        "td_key_missing_error": (
            "کلید API تنظیم نشده. آن را در Streamlit Secrets (نام: twelvedata_api_key) "
            "یا متغیر محیطی TWELVEDATA_API_KEY قرار دهید."
        ),
        "td_error": "خطای Twelve Data: {err}",
        "td_conn_error": "خطای اتصال: {err}",
        "autorefresh_missing_warning": "برای به‌روزرسانی خودکار، پکیج streamlit-autorefresh را نصب کنید.",
        "no_data_info": (
            "این داشبورد فقط با داده‌ی واقعی/آنلاین کار می‌کند و داده‌ی ساختگی نمایش نمی‌دهد. "
            "از نوار کناری، کلید Twelve Data را تنظیم کنید و روی «📡 دریافت داده از Twelve Data» "
            "بزنید، یا یک فایل CSV واقعی آپلود کنید."
        ),

        "chart_layers_header": "🧩 لایه‌های نمایش روی چارت",
        "rsi_panel_checkbox": "پنل RSI",
        "macd_panel_checkbox": "پنل MACD",
        "layer_order_blocks": "Order Blocks",
        "layer_fvg": "Fair Value Gaps",
        "layer_supply_demand": "Supply / Demand",
        "layer_liquidity": "نقدینگی (Liquidity)",
        "layer_support_resistance": "حمایت / مقاومت",

        "risk_mgmt_header": "💰 مدیریت ریسک و سرمایه",
        "account_balance_label": "موجودی حساب ($)",
        "risk_pct_label": "درصد ریسک هر معامله (%)",
        "rr_target_label": "نسبت ریسک به ریوارد هدف",
        "max_daily_loss_label": "حد ضرر روزانه (%) — توقف خودکار معاملات",
        "max_drawdown_label": "حداکثر افت سرمایه مجاز (Max Drawdown %)",
        "max_open_trades_label": "حداکثر تعداد معاملات باز هم‌زمان",

        "smc_sensitivity_header": "🎯 حساسیت موتور SMC",
        "swing_lookback_label": "Swing Lookback",
        "ob_lookback_label": "Order Block Lookback",
        "fvg_gap_label": "حداقل درصد شکاف FVG",

        "ml_model_header": "🤖 مدل امتیازدهی سیگنال (ML)",
        "ml_model_caption": (
            "یک مدل طبقه‌بندی (نه پیش‌بینی قیمت) که از روی فیچرهای همین موتور "
            "SMC یاد گرفته چه ترکیبی از سیگنال‌ها تاریخاً بیشتر به TP رسیده‌اند. "
            "برای ساخت مدل: `python scripts/train_signal_model.py --csv <داده‌ی شما>`"
        ),
        "ml_model_path_label": "مسیر فایل مدل (.joblib)",
        "ml_enable_checkbox": "فعال‌سازی امتیاز ML روی سیگنال‌ها",
        "ml_min_prob_label": "حداقل احتمال مدل برای نمایش سیگنال",
        "ml_min_prob_help": "۰ یعنی فیلتر نشود؛ فقط برای اطلاع نمایش داده می‌شود.",
        "ml_loaded_success": "مدل ML بارگذاری شد (backend={backend})",
        "ml_not_found_error": (
            "فایل مدل پیدا نشد: {path} — ابتدا با دستور "
            "`python scripts/train_signal_model.py --csv <داده‌ی شما>` یک مدل بسازید."
        ),
        "ml_load_failed_error": "بارگذاری مدل شکست خورد: {err}",

        "cl_caption": "یادگیری مستمر: مدل از روی نتایج واقعی معاملات (بک‌تست/دمو) بازآموزی می‌شود.",
        "cl_retrain_btn": "🔁 بازآموزی مدل از نتایج واقعی",
        "cl_logged_info": "{n} نتیجه‌ی معامله‌ی واقعی جدید در لاگ آموزش ثبت شد.",
        "cl_retraining_spinner": "در حال بازآموزی موتور Ensemble ...",
        "cl_promoted_success": "مدل جدید با {n} نمونه بازآموزی و جایگزین شد (AUC≈{auc:.2f}).",
        "cl_rejected_warning": "مدل جدید نسبت به مدل قبلی ضعیف‌تر بود؛ جایگزین نشد.",
        "cl_insufficient_data_warning": "فقط {n} نمونه در لاگ موجود است؛ برای بازآموزی معتبر باید بیشتر معامله/بک‌تست کنید.",

        "ai_decision_expander": "🧠 موتور تصمیم‌گیری هوش مصنوعی (Ensemble)",
        "ai_decision_probability": "احتمال موفقیت",
        "ai_decision_confidence": "Confidence Score",
        "ai_decision_agreement": "توافق مدل‌ها",
        "ai_decision_per_model_caption": "شکست تصمیم به تفکیک هر مدل عضو:",
        "ai_decision_model_col": "مدل",
        "ai_decision_model_weight_col": "وزن در تصمیم نهایی",
        "ai_decision_model_proba_col": "احتمال این مدل",
        "ai_decision_reasons_caption": "مهم‌ترین دلایل این تصمیم:",

        "run_backtest_btn": "🚀 اجرای بک‌تست",

        # --- حساب دمو و معامله‌گری خودکار (نوار کناری) ---
        "demo_account_header": "🧾 حساب دمو (بدون نیاز به بروکر)",
        "demo_initial_balance_label": "موجودی اولیه حساب دمو ($)",
        "demo_reset_btn": "♻️ بازنشانی حساب دمو",
        "demo_reset_success": "حساب دمو با موجودی جدید بازنشانی شد.",
        "auto_trading_header": "🤖 معاملات خودکار بر اساس هوش مصنوعی",
        "auto_trading_enable_checkbox": "فعال‌سازی ورود خودکار به معامله",
        "auto_trading_min_conf_label": "حداقل درصد موفقیت/اطمینان برای ورود",
        "auto_trading_use_ml_checkbox": "اولویت با امتیاز مدل ML (در صورت فعال بودن آن)",
        "auto_trading_hint": (
            "وقتی فعال باشد، به‌ازای هر سیگنال جدید که درصد اطمینان (یا امتیاز ML) آن از "
            "مقدار تعیین‌شده بیشتر باشد، یک معامله در «حساب دمو» با حجم محاسبه‌شده بر اساس "
            "مدیریت ریسک، به‌همراه SL/TP خودکار باز می‌شود."
        ),
        "auto_trading_halted_warning": (
            "⛔ معاملات خودکار به‌دلیل رسیدن به حد ضرر روزانه ({loss:.2f}%) امروز متوقف شده است."
        ),
        "auto_trade_opened_toast": "✅ معامله خودکار باز شد: {direction} حجم {volume} @ {price:,.2f}",

        # --- تب‌ها ---
        "tab_live": "📊 تحلیل زنده",
        "tab_backtest": "🧪 بک‌تست حرفه‌ای",
        "tab_demo": "🧾 حساب دمو",
        "tab_guide": "📚 راهنما",

        # --- تب تحلیل زنده ---
        "signal_direction_long": "خرید (LONG)",
        "signal_direction_short": "فروش (SHORT)",
        "signal_entry": "Entry",
        "signal_sl": "Stop Loss",
        "signal_tp": "Take Profit",
        "signal_rr_conf": "R/R | اطمینان",
        "signal_ml_score": "امتیاز مدل ML",
        "signal_reasons_expander": "📋 دلایل سیگنال",
        "signal_none_text": (
            "در این لحظه هیچ سیگنال معتبری (بر اساس آخرین ۳۰۰ کندل و تنظیمات "
            "فعلی) یافت نشد. می‌توانید حساسیت موتور SMC را از نوار کناری افزایش دهید."
        ),
        "market_card_high24": "بالاترین قیمت (۲۴ کندل)",
        "market_card_low24": "پایین‌ترین قیمت (۲۴ کندل)",
        "market_card_rsi": "RSI فعلی",
        "market_card_atr": "ATR فعلی",
        "chart_pro_header": "چارت حرفه‌ای (ساختار نسخه ۱)",
        "chart_layers_header2": "لایه‌های تحلیلی (SMC / ICT / اندیکاتورها)",

        # --- تب بک‌تست ---
        "backtest_results_header": "نتایج بک‌تست",
        "backtest_hint": "تنظیمات را از نوار کناری انتخاب کنید و روی «🚀 اجرای بک‌تست» بزنید.",
        "metric_total_trades": "تعداد معاملات",
        "metric_win_rate": "Win Rate",
        "metric_profit_factor": "Profit Factor",
        "metric_net_profit": "سود خالص",
        "metric_sharpe": "Sharpe Ratio",
        "metric_max_dd": "Max Drawdown",
        "metric_avg_win_loss": "میانگین برد / باخت",
        "metric_expectancy": "Expectancy",
        "trades_list_header": "#### 📋 لیست معاملات",
        "download_trades_btn": "⬇️ دانلود CSV معاملات",
        "backtest_no_trades_warning": (
            "در این بازه‌ی داده و تنظیمات، معامله‌ای شکل نگرفت. حساسیت موتور SMC را "
            "از نوار کناری افزایش دهید (Order Block/Swing Lookback کمتر، FVG Gap کمتر)."
        ),
        "col_id": "شناسه",
        "col_direction": "جهت",
        "col_open_time": "زمان ورود",
        "col_close_time": "زمان خروج",
        "col_entry": "ورود",
        "col_exit": "خروج",
        "col_sl": "SL",
        "col_tp": "TP",
        "col_volume": "حجم",
        "col_profit": "سود/زیان ($)",
        "col_reason": "دلیل خروج",
        "direction_buy": "خرید",
        "direction_sell": "فروش",

        # --- تب حساب دمو ---
        "demo_tab_header": "🧾 حساب دمو — معاملات شبیه‌سازی‌شده",
        "demo_tab_caption": (
            "این حساب کاملاً داخلی و بدون اتصال به بروکر است؛ فقط برای تمرین و مشاهده‌ی عملکرد "
            "سیگنال‌های هوش مصنوعی روی داده‌ی واقعی بازار استفاده می‌شود."
        ),
        "demo_metric_balance": "موجودی (Balance)",
        "demo_metric_equity": "دارایی (Equity)",
        "demo_metric_margin": "مارجین استفاده‌شده",
        "demo_metric_free_margin": "مارجین آزاد",
        "demo_metric_floating_pnl": "سود/زیان شناور",
        "demo_metric_win_rate": "نرخ موفقیت (Win Rate)",
        "demo_metric_total_trades": "تعداد کل معاملات",
        "demo_metric_max_dd": "حداکثر افت سرمایه",
        "demo_pnl_header": "سود و زیان دوره‌ای",
        "demo_pnl_today": "امروز",
        "demo_pnl_week": "۷ روز اخیر",
        "demo_pnl_month": "۳۰ روز اخیر",
        "demo_open_positions_header": "📂 معاملات باز",
        "demo_no_open_positions": "در حال حاضر معامله‌ی بازی در حساب دمو وجود ندارد.",
        "demo_history_header": "📜 تاریخچه‌ی معاملات بسته‌شده",
        "demo_no_history": "هنوز هیچ معامله‌ای بسته نشده است.",
        "demo_equity_chart_header": "📈 نمودار رشد سرمایه (Equity Curve)",
        "demo_status_auto_on": "🟢 معاملات خودکار فعال است (حداقل اطمینان: {conf:.0f}٪)",
        "demo_status_auto_off": "⚪ معاملات خودکار غیرفعال است — فقط از نوار کناری فعال کنید.",
        "col_confidence": "اطمینان",
        "col_current_price": "قیمت فعلی",
        "col_floating_pnl": "سود/زیان شناور ($)",

        # --- تب راهنما ---
        "guide_content": """
### چطور از این داشبورد استفاده کنم؟

1. **منبع داده** را از نوار کناری انتخاب کنید: اتصال زنده به Twelve Data (پیش‌فرض) یا آپلود فایل CSV
   واقعی شخصی. این داشبورد دیگر داده‌ی ساختگی/شبیه‌سازی‌شده نمایش نمی‌دهد.
2. **چارت حرفه‌ای (ساختار نسخه ۱)** نمای اصلی TradingView-مانند است: نوار بالایی (نماد/قیمت/درصد
   تغییر/تایم‌فریم)، ابزار ترسیم سمت چپ، پنل اطلاعات سمت راست (OHLC، Spread، شمارش معکوس کندل،
   وضعیت اتصال) و نوار پایین (Volume، ساعت بازار).
3. **لایه‌های تحلیلی (SMC/ICT)** زیر آن، همان Order Block، FVG، Supply/Demand، نقدینگی و حمایت/مقاومت
   را روی چارت تحلیلی (Plotly) نمایش می‌دهد و قابل فیلتر است.
4. **مدیریت ریسک** موجودی حساب، درصد ریسک هر معامله، نسبت ریسک‌به‌ریوارد و حد ضرر روزانه را مشخص می‌کند —
   این مقادیر مستقیماً روی حجم پیشنهادی معامله، بک‌تست و حساب دمو اثر می‌گذارند.
5. **حساب دمو** یک حساب کاملاً داخلی و شبیه‌سازی‌شده با موجودی اولیه‌ی قابل‌تنظیم است؛ نیازی به اتصال
   به بروکر ندارد. موجودی، دارایی (Equity)، مارجین، مارجین آزاد و سود/زیان لحظه‌ای در تب «حساب دمو»
   نمایش داده می‌شود و تاریخچه‌ی کامل معاملات ثبت می‌شود.
6. **معاملات خودکار** را از نوار کناری فعال کنید و حداقل درصد اطمینان لازم برای ورود را تعیین کنید؛
   هر سیگنالی که از این آستانه بالاتر باشد، به‌طور خودکار در حساب دمو با حجم مناسب (بر اساس مدیریت
   سرمایه) و SL/TP از پیش تعیین‌شده باز می‌شود. اگر ضرر روزانه به حد تعیین‌شده برسد، ورود به معاملات
   جدید به‌طور خودکار متوقف می‌شود.
7. **حساسیت موتور SMC** کنترل می‌کند موتور چقدر «سخت‌گیر» باشد؛ اگر سیگنال یا معامله‌ای شکل نمی‌گیرد،
   Lookback ها را کم و حداقل شکاف FVG را کاهش دهید.
8. تب **بک‌تست حرفه‌ای** را برای اجرای استراتژی روی کل بازه‌ی داده و مشاهده‌ی Equity Curve، Drawdown
   و لیست کامل معاملات استفاده کنید.

### محدودیت‌های شناخته‌شده

- اتصال زنده به **MetaTrader 5** فقط روی ویندوز و در اجرای محلی (خارج از این داشبورد ابری) کار می‌کند؛
  برای جزئیات به `docs/INSTALL.md` مراجعه کنید.
- «به‌روزرسانی خودکار» با فاصله‌ی ۳۰ ثانیه بازه‌ی جدید را از Twelve Data می‌گیرد؛ سقف تعداد درخواست
  بستگی به پلن حساب شما در Twelve Data دارد.
- **حساب دمو** یک شبیه‌سازی محلی در همین مرورگر/سشن است (نه یک حساب واقعی بروکر) و با رفرش کامل صفحه
  یا بستن تب ممکن است بازنشانی شود.
- مقدار **Spread** چون Twelve Data قیمت Mid برمی‌گرداند، از یک بروکر واقعی در دسترس نیست.
""",
    },
    "en": {
        # --- general ---
        "app_title": "📈 XAUUSD Trading Suite",
        "app_subtitle": "Live analysis dashboard · SMC/ICT + classic indicators · Hasan Javadi · Telegram: @mr_hj369",
        "footer_text": "⚠️ This software is an analytical/educational tool only and does not constitute financial "
                        "advice. Demo account trades are fully simulated with no real money. Live MT5 connection "
                        "is not available on this cloud dashboard (Windows only).",

        # --- sidebar: general ---
        "sidebar_title": "⚙️ Settings",
        "lang_switch_label": "🌐 Language",

        "data_source_header": "📥 Data Source (live/real only)",
        "data_source_radio_label": "Where should the data come from?",
        "data_source_option_live": "Twelve Data API (live)",
        "data_source_option_csv": "Upload CSV",
        "csv_uploader_label": "CSV file",
        "td_symbol_label": "Symbol (Twelve Data format)",
        "td_timeframe_label": "Timeframe",
        "td_fetch_btn": "📡 Fetch data from Twelve Data",
        "auto_refresh_checkbox": "🔄 Auto-refresh (live chart)",
        "auto_refresh_interval_label": "Refresh interval (seconds)",
        "live_status_live": "🟢 Live — last updated: {ts}",
        "live_status_stale": "🟡 Last data (not live-connected): {ts}",
        "api_key_guide_expander": "API key guide",
        "api_key_guide_text": (
            "Do not hardcode the API key in code. Set it in Streamlit Cloud → "
            "**Settings → Secrets** as `twelvedata_api_key`, or set the "
            "`TWELVEDATA_API_KEY` environment variable when running locally. Details: docs/DEPLOY.md"
        ),
        "csv_loaded_success": "{n} candles loaded from your file.",
        "td_fetched_success": "{n} candles fetched.",
        "td_key_missing_error": (
            "API key is not set. Add it to Streamlit Secrets (name: twelvedata_api_key) "
            "or the TWELVEDATA_API_KEY environment variable."
        ),
        "td_error": "Twelve Data error: {err}",
        "td_conn_error": "Connection error: {err}",
        "autorefresh_missing_warning": "Install the streamlit-autorefresh package to enable auto-refresh.",
        "no_data_info": (
            "This dashboard only works with real/live data — it never shows synthetic data. "
            "Set your Twelve Data key in the sidebar and click \"📡 Fetch data from Twelve Data\", "
            "or upload a real CSV file."
        ),

        "chart_layers_header": "🧩 Chart display layers",
        "rsi_panel_checkbox": "RSI panel",
        "macd_panel_checkbox": "MACD panel",
        "layer_order_blocks": "Order Blocks",
        "layer_fvg": "Fair Value Gaps",
        "layer_supply_demand": "Supply / Demand",
        "layer_liquidity": "Liquidity",
        "layer_support_resistance": "Support / Resistance",

        "risk_mgmt_header": "💰 Risk & Money Management",
        "account_balance_label": "Account balance ($)",
        "risk_pct_label": "Risk per trade (%)",
        "rr_target_label": "Target risk/reward ratio",
        "max_daily_loss_label": "Daily loss limit (%) — auto-stop trading",
        "max_drawdown_label": "Max allowed drawdown (%)",
        "max_open_trades_label": "Max simultaneous open trades",

        "smc_sensitivity_header": "🎯 SMC Engine Sensitivity",
        "swing_lookback_label": "Swing Lookback",
        "ob_lookback_label": "Order Block Lookback",
        "fvg_gap_label": "Minimum FVG gap (%)",

        "ml_model_header": "🤖 ML Signal Scoring Model",
        "ml_model_caption": (
            "A classification model (not a price predictor) trained on this SMC engine's own features, "
            "learning which combination of signals has historically reached TP more often. "
            "To build a model: `python scripts/train_signal_model.py --csv <your data>`"
        ),
        "ml_model_path_label": "Model file path (.joblib)",
        "ml_enable_checkbox": "Enable ML score on signals",
        "ml_min_prob_label": "Minimum model probability to show signal",
        "ml_min_prob_help": "0 means no filtering; shown for information only.",
        "ml_loaded_success": "ML model loaded (backend={backend})",
        "ml_not_found_error": (
            "Model file not found: {path} — first build a model with "
            "`python scripts/train_signal_model.py --csv <your data>`"
        ),
        "ml_load_failed_error": "Failed to load model: {err}",

        "cl_caption": "Continuous learning: the model retrains from real trade outcomes (backtest/demo).",
        "cl_retrain_btn": "🔁 Retrain model from real results",
        "cl_logged_info": "{n} new real trade outcomes logged for training.",
        "cl_retraining_spinner": "Retraining the Ensemble engine ...",
        "cl_promoted_success": "New model retrained on {n} samples and promoted (AUC≈{auc:.2f}).",
        "cl_rejected_warning": "New model performed worse than the current one; not promoted.",
        "cl_insufficient_data_warning": "Only {n} samples logged so far; trade/backtest more for a meaningful retrain.",

        "ai_decision_expander": "🧠 AI Decision Engine (Ensemble)",
        "ai_decision_probability": "Success probability",
        "ai_decision_confidence": "Confidence score",
        "ai_decision_agreement": "Model agreement",
        "ai_decision_per_model_caption": "Decision breakdown per member model:",
        "ai_decision_model_col": "Model",
        "ai_decision_model_weight_col": "Weight in final decision",
        "ai_decision_model_proba_col": "This model's probability",
        "ai_decision_reasons_caption": "Top reasons behind this decision:",

        "run_backtest_btn": "🚀 Run Backtest",

        # --- demo account & auto trading (sidebar) ---
        "demo_account_header": "🧾 Demo Account (no broker required)",
        "demo_initial_balance_label": "Demo account initial balance ($)",
        "demo_reset_btn": "♻️ Reset demo account",
        "demo_reset_success": "Demo account has been reset with the new balance.",
        "auto_trading_header": "🤖 AI-Based Automated Trading",
        "auto_trading_enable_checkbox": "Enable automatic trade entry",
        "auto_trading_min_conf_label": "Minimum confidence/success % to enter",
        "auto_trading_use_ml_checkbox": "Prefer ML score over rule-based confidence (if model enabled)",
        "auto_trading_hint": (
            "When enabled, every new signal whose confidence (or ML score) exceeds the threshold "
            "automatically opens a trade in the Demo Account, with position size computed from your "
            "risk settings and automatic SL/TP."
        ),
        "auto_trading_halted_warning": (
            "⛔ Automated trading has been stopped today after hitting the daily loss limit ({loss:.2f}%)."
        ),
        "auto_trade_opened_toast": "✅ Auto trade opened: {direction} volume {volume} @ {price:,.2f}",

        # --- tabs ---
        "tab_live": "📊 Live Analysis",
        "tab_backtest": "🧪 Pro Backtest",
        "tab_demo": "🧾 Demo Account",
        "tab_guide": "📚 Guide",

        # --- live tab ---
        "signal_direction_long": "BUY (LONG)",
        "signal_direction_short": "SELL (SHORT)",
        "signal_entry": "Entry",
        "signal_sl": "Stop Loss",
        "signal_tp": "Take Profit",
        "signal_rr_conf": "R/R | Confidence",
        "signal_ml_score": "ML Model Score",
        "signal_reasons_expander": "📋 Signal reasons",
        "signal_none_text": (
            "No valid signal found right now (based on the last 300 candles and current settings). "
            "You can increase the SMC engine sensitivity from the sidebar."
        ),
        "market_card_high24": "24-candle high",
        "market_card_low24": "24-candle low",
        "market_card_rsi": "Current RSI",
        "market_card_atr": "Current ATR",
        "chart_pro_header": "Professional Chart (v1 layout)",
        "chart_layers_header2": "Analytical layers (SMC / ICT / indicators)",

        # --- backtest tab ---
        "backtest_results_header": "Backtest Results",
        "backtest_hint": "Choose your settings in the sidebar and click \"🚀 Run Backtest\".",
        "metric_total_trades": "Total trades",
        "metric_win_rate": "Win Rate",
        "metric_profit_factor": "Profit Factor",
        "metric_net_profit": "Net profit",
        "metric_sharpe": "Sharpe Ratio",
        "metric_max_dd": "Max Drawdown",
        "metric_avg_win_loss": "Avg win / loss",
        "metric_expectancy": "Expectancy",
        "trades_list_header": "#### 📋 Trade list",
        "download_trades_btn": "⬇️ Download trades CSV",
        "backtest_no_trades_warning": (
            "No trades were formed with this data range and settings. Increase the SMC engine sensitivity "
            "from the sidebar (lower Order Block/Swing Lookback, lower FVG gap)."
        ),
        "col_id": "ID",
        "col_direction": "Direction",
        "col_open_time": "Open time",
        "col_close_time": "Close time",
        "col_entry": "Entry",
        "col_exit": "Exit",
        "col_sl": "SL",
        "col_tp": "TP",
        "col_volume": "Volume",
        "col_profit": "Profit/Loss ($)",
        "col_reason": "Close reason",
        "direction_buy": "Buy",
        "direction_sell": "Sell",

        # --- demo account tab ---
        "demo_tab_header": "🧾 Demo Account — Simulated Trading",
        "demo_tab_caption": (
            "This account is fully internal and not connected to any broker; it exists to practice and "
            "observe how the AI signals would have performed on real market data."
        ),
        "demo_metric_balance": "Balance",
        "demo_metric_equity": "Equity",
        "demo_metric_margin": "Used margin",
        "demo_metric_free_margin": "Free margin",
        "demo_metric_floating_pnl": "Floating P/L",
        "demo_metric_win_rate": "Win Rate",
        "demo_metric_total_trades": "Total trades",
        "demo_metric_max_dd": "Max drawdown",
        "demo_pnl_header": "Periodic P/L",
        "demo_pnl_today": "Today",
        "demo_pnl_week": "Last 7 days",
        "demo_pnl_month": "Last 30 days",
        "demo_open_positions_header": "📂 Open positions",
        "demo_no_open_positions": "There are currently no open positions in the demo account.",
        "demo_history_header": "📜 Closed trade history",
        "demo_no_history": "No trades have been closed yet.",
        "demo_equity_chart_header": "📈 Equity Growth Curve",
        "demo_status_auto_on": "🟢 Automated trading is ON (min confidence: {conf:.0f}%)",
        "demo_status_auto_off": "⚪ Automated trading is OFF — enable it from the sidebar.",
        "col_confidence": "Confidence",
        "col_current_price": "Current price",
        "col_floating_pnl": "Floating P/L ($)",

        # --- guide tab ---
        "guide_content": """
### How do I use this dashboard?

1. Choose your **data source** from the sidebar: live Twelve Data connection (default) or upload your own
   real CSV file. This dashboard never shows synthetic/fake data.
2. The **Professional Chart (v1 layout)** is the main TradingView-like view: top bar (symbol/price/change
   %/timeframe), drawing tools on the left, an info panel on the right (OHLC, spread, candle countdown,
   connection status), and a bottom bar (volume, market hours).
3. **Analytical layers (SMC/ICT)** below it show Order Blocks, FVGs, Supply/Demand, liquidity, and
   support/resistance on the analytical (Plotly) chart, and are filterable.
4. **Risk management** sets account balance, risk per trade, target risk/reward, and the daily loss limit —
   these directly drive the suggested position size, backtests, and the demo account.
5. The **Demo Account** is a fully internal, simulated account with an adjustable initial balance; no broker
   connection required. Balance, Equity, margin, free margin and live P/L are shown in the "Demo Account"
   tab, and a full trade history is recorded.
6. Enable **Automated Trading** from the sidebar and set the minimum confidence % required to enter; any
   signal above that threshold automatically opens a trade in the demo account with the right position size
   (based on your risk settings) and pre-set SL/TP. If the daily loss limit is hit, new automated entries
   stop automatically for the rest of the day.
7. **SMC engine sensitivity** controls how strict the engine is; if no signal or trade forms, lower the
   lookback values and the minimum FVG gap.
8. Use the **Pro Backtest** tab to run the strategy across the whole data range and see the Equity Curve,
   Drawdown, and the full trade list.

### Known limitations

- A live **MetaTrader 5** connection only works on Windows in a local run (outside this cloud dashboard);
  see `docs/INSTALL.md` for details.
- "Auto-refresh" fetches a new bar from Twelve Data every 30 seconds; your request cap depends on your
  Twelve Data plan.
- The **Demo Account** is a local simulation within this browser/session (not a real broker account) and may
  reset on a full page refresh or when the tab is closed.
- Because Twelve Data returns mid prices, a real **spread** value is not available from a real broker feed.
""",
    },
}
