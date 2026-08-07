"""
داشبورد وب XAUUSD Trading Suite — نسخه Streamlit.

این فایل طوری طراحی شده که با یک `git push` روی گیت‌هاب و اتصال به
Streamlit Community Cloud (share.streamlit.io)، بدون نیاز کاربر به نصب
هیچ‌چیزی، از طریق یک لینک عمومی باز شود و خودش اجرا/رندر شود.

اجرای محلی:
    streamlit run streamlit_app.py

نکته: بخش اتصال زنده به MT5 روی سرورهای ابری (لینوکس) کار نمی‌کند، چون
پکیج رسمی MetaTrader5 فقط روی ویندوز اجرا می‌شود. این داشبورد برای تحلیل،
بک‌تست و مشاهده‌ی چارت/سیگنال روی داده‌ی تاریخی (CSV) ساخته شده است.
"""
from __future__ import annotations

import io
import os

import pandas as pd
import streamlit as st
import yaml

from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.strategy.ai_strategy import AIStrategy, EnsembleStrategy
from src.backtest.engine import BacktestEngine, BacktestConfig
from src.risk_management.position_sizing import SymbolSpec
from src.risk_management.trade_manager import RiskConfig
from src.chart.chart_app import build_figure
from src.connectors.twelvedata_connector import fetch_time_series, TwelveDataError
from src.price_action.candlestick_patterns import detect_all_patterns
from src.ml.feature_engineering import build_features, clean_features_labels
from src.ml.labeling import triple_barrier_labels, label_distribution
from src.ml.model import MLSignalModel

MODEL_PATH = "models/xauusd_model.joblib"

st.set_page_config(page_title="XAUUSD Trading Suite", layout="wide", page_icon="📈")

DEFAULT_CONFIG_PATH = "config/config.yaml"
DEFAULT_SAMPLE_CSV = "data/sample_xauusd_h1.csv"


# ---------------------------------------------------------------------- #
# بارگذاری تنظیمات و داده
# ---------------------------------------------------------------------- #
@st.cache_data
def load_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_csv_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes))
    time_col = "datetime" if "datetime" in df.columns else "time"
    df = df.rename(columns={time_col: "time"})
    df["time"] = pd.to_datetime(df["time"])
    return df.sort_values("time").reset_index(drop=True)


@st.cache_data
def load_default_sample() -> pd.DataFrame:
    df = pd.read_csv(DEFAULT_SAMPLE_CSV, parse_dates=["datetime"])
    return df.rename(columns={"datetime": "time"}).sort_values("time").reset_index(drop=True)


# ---------------------------------------------------------------------- #
# نوار کناری: تنظیمات
# ---------------------------------------------------------------------- #
st.sidebar.title("⚙️ تنظیمات XAUUSD Trading Suite")

st.sidebar.subheader("منبع داده")
data_source = st.sidebar.radio(
    "داده از کجا بیاید؟",
    ["داده نمونه (شبیه‌سازی‌شده)", "آپلود CSV", "Twelve Data API (زنده)"],
    index=0,
)

uploaded = None
td_symbol, td_interval, td_bars, td_fetch_btn = None, None, None, False

if data_source == "آپلود CSV":
    uploaded = st.sidebar.file_uploader("فایل CSV", type=["csv"])
elif data_source == "Twelve Data API (زنده)":
    td_symbol = st.sidebar.text_input("نماد (فرمت Twelve Data)", value="XAU/USD")
    td_interval = st.sidebar.selectbox("تایم‌فریم", ["M15", "M30", "H1", "H4", "D1"], index=2)
    td_bars = st.sidebar.slider("تعداد کندل دریافتی", 100, 2000, 500, step=100)
    td_fetch_btn = st.sidebar.button("📡 دریافت داده از Twelve Data", use_container_width=True)
    with st.sidebar.expander("راهنمای کلید API"):
        st.write(
            "کلید API را در این کد وارد نکنید. آن را در Streamlit Cloud → "
            "**Settings → Secrets** با نام `twelvedata_api_key` ثبت کنید، یا هنگام اجرای "
            "محلی متغیر محیطی `TWELVEDATA_API_KEY` را تنظیم کنید. جزئیات: docs/DEPLOY.md"
        )

n_bars_display = st.sidebar.slider("تعداد کندل نمایش در چارت", 100, 2000, 500, step=50)

st.sidebar.markdown("---")
st.sidebar.subheader("مدیریت ریسک")
account_balance = st.sidebar.number_input("موجودی حساب ($)", value=10_000.0, step=500.0)
risk_pct = st.sidebar.slider("درصد ریسک هر معامله (%)", 0.25, 5.0, 1.0, step=0.25)
rr_target = st.sidebar.slider("نسبت ریسک به ریوارد هدف", 1.0, 5.0, 2.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.subheader("حساسیت موتور SMC")
swing_lookback = st.sidebar.slider("Swing Lookback", 2, 10, 5)
order_block_lookback = st.sidebar.slider("Order Block Lookback", 5, 50, 20)
fvg_min_gap_pct = st.sidebar.slider("حداقل درصد شکاف FVG", 0.0, 0.2, 0.02, step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("موتور تحلیل")
strategy_mode = st.sidebar.radio(
    "کدام موتور سیگنال بدهد؟",
    ["SMC/ICT (قانون‌محور)", "هوش مصنوعی (یادگیری ماشین)", "ادغامی (SMC + AI)"],
    index=0,
)
ai_min_confidence = None
ensemble_agree_mode = "agreement"
if strategy_mode != "SMC/ICT (قانون‌محور)":
    ai_min_confidence = st.sidebar.slider("حداقل اطمینان مدل AI (%)", 40, 90, 60, step=5)
    if strategy_mode == "ادغامی (SMC + AI)":
        ensemble_agree_mode = st.sidebar.selectbox(
            "حالت ادغام", ["agreement (فقط تایید دوسویه)", "any (هرکدام)"], index=0,
        ).split(" ")[0]

run_backtest_btn = st.sidebar.button("🚀 اجرای بک‌تست", use_container_width=True)

# ---------------------------------------------------------------------- #
# آماده‌سازی داده و config
# ---------------------------------------------------------------------- #
config = load_config()
config["risk"]["account_balance"] = account_balance
config["risk"]["risk_per_trade_pct"] = risk_pct
config["risk"]["reward_risk_ratio"] = rr_target
config["smc"]["swing_lookback"] = swing_lookback
config["smc"]["order_block_lookback"] = order_block_lookback
config["smc"]["fvg_min_gap_pct"] = fvg_min_gap_pct
if ai_min_confidence is not None:
    config.setdefault("ai", {})["min_confidence_pct"] = ai_min_confidence

def get_twelvedata_key() -> str | None:
    """کلید را ابتدا از Streamlit Secrets و سپس از متغیر محیطی می‌خواند؛ هرگز hardcode نمی‌شود."""
    try:
        if "twelvedata_api_key" in st.secrets:
            return st.secrets["twelvedata_api_key"]
    except Exception:
        pass
    return os.environ.get("TWELVEDATA_API_KEY")


if uploaded is not None:
    df_raw = load_csv_from_bytes(uploaded.read())
    st.sidebar.success(f"{len(df_raw)} کندل از فایل شما بارگذاری شد.")
elif data_source == "Twelve Data API (زنده)":
    if td_fetch_btn:
        api_key = get_twelvedata_key()
        if not api_key:
            st.sidebar.error(
                "کلید API تنظیم نشده. آن را در Streamlit Secrets (نام: twelvedata_api_key) "
                "یا متغیر محیطی TWELVEDATA_API_KEY قرار دهید."
            )
        else:
            try:
                with st.spinner(f"در حال دریافت {td_symbol} از Twelve Data..."):
                    st.session_state["td_data"] = fetch_time_series(
                        symbol=td_symbol, interval=td_interval,
                        outputsize=td_bars, api_key=api_key,
                    )
                st.sidebar.success(f"{len(st.session_state['td_data'])} کندل دریافت شد.")
            except TwelveDataError as e:
                st.sidebar.error(f"خطای Twelve Data: {e}")
            except Exception as e:
                st.sidebar.error(f"خطای اتصال: {e}")

    if "td_data" in st.session_state:
        df_raw = st.session_state["td_data"]
    else:
        st.sidebar.info("روی «دریافت داده از Twelve Data» بزنید تا داده زنده بیاید.")
        df_raw = load_default_sample()
else:
    df_raw = load_default_sample()
    st.sidebar.info("از داده نمونه (شبیه‌سازی‌شده) استفاده می‌شود.")

df = compute_all_indicators(df_raw, config)

# ------------------------------------------------------------------ #
# ساخت موتور تحلیل بر اساس انتخاب کاربر (SMC / AI / ادغامی)
# ------------------------------------------------------------------ #
def load_or_get_model() -> MLSignalModel | None:
    if "ml_model" in st.session_state:
        return st.session_state["ml_model"]
    if os.path.exists(MODEL_PATH):
        model = MLSignalModel.load(MODEL_PATH)
        st.session_state["ml_model"] = model
        return model
    return None


if strategy_mode != "SMC/ICT (قانون‌محور)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("مدل یادگیری ماشین")
    model = load_or_get_model()
    if model is not None:
        st.sidebar.success("مدل آماده (از قبل آموزش‌دیده یا در جلسه فعلی آموزش داده شده) ✅")
    else:
        st.sidebar.warning("هنوز مدلی آموزش داده نشده.")

    if st.sidebar.button("🧠 آموزش مدل روی داده فعلی", use_container_width=True):
        with st.spinner("در حال آموزش مدل روی داده فعلی (ممکن است چند ثانیه طول بکشد)..."):
            df_train = detect_all_patterns(df)
            ai_cfg = config.get("ai", {})
            labels = triple_barrier_labels(
                df_train, df_train["atr"],
                tp_atr_mult=ai_cfg.get("tp_atr_mult", 2.0),
                sl_atr_mult=ai_cfg.get("sl_atr_mult", 1.0),
                max_horizon_bars=ai_cfg.get("max_horizon_bars", 20),
            )
            dist = label_distribution(labels)
            features = build_features(df_train)
            X, y = clean_features_labels(features, labels)

            new_model = MLSignalModel(model_type=ai_cfg.get("model_type", "gradient_boosting"))
            report = new_model.train(X, y, test_size=ai_cfg.get("test_size", 0.2))
            st.session_state["ml_model"] = new_model
            st.session_state["ml_report"] = report
            st.session_state["ml_label_dist"] = dist
        model = new_model
        st.sidebar.success(
            f"آموزش تمام شد — دقت تست: {report.test_accuracy * 100:.1f}% "
            f"({report.n_train} نمونه آموزش / {report.n_test} نمونه تست)"
        )

    if "ml_report" in st.session_state:
        with st.sidebar.expander("جزئیات آخرین آموزش مدل"):
            r = st.session_state["ml_report"]
            d = st.session_state.get("ml_label_dist", {})
            st.write(f"توزیع برچسب‌ها: صعودی {d.get('bullish_pct','?')}% / "
                     f"نزولی {d.get('bearish_pct','?')}% / خنثی {d.get('neutral_pct','?')}%")
            st.write(f"دقت آموزش: {r.train_accuracy*100:.1f}% | دقت تست: {r.test_accuracy*100:.1f}%")
            st.caption("⚠️ اختلاف زیاد بین دقت آموزش و تست یعنی مدل overfit شده — "
                       "با داده تاریخی بیشتر و واقعی‌تر (نه داده نمونه شبیه‌سازی‌شده) بهبود می‌یابد.")

    if model is None:
        st.warning("برای استفاده از موتور AI/ادغامی، ابتدا از نوار کناری روی "
                   "«آموزش مدل روی داده فعلی» بزنید.")
        st.stop()

if strategy_mode == "SMC/ICT (قانون‌محور)":
    strategy = SMCConfluenceStrategy(config)
elif strategy_mode == "هوش مصنوعی (یادگیری ماشین)":
    strategy = AIStrategy(config, model)
else:
    strategy = EnsembleStrategy(config, model, mode=ensemble_agree_mode)

df = strategy.prepare(df)

# ---------------------------------------------------------------------- #
# هدر و سیگنال فعلی
# ---------------------------------------------------------------------- #
st.title("📈 XAUUSD Trading Suite — داشبورد تحلیل زنده")
st.caption("توسعه‌دهنده: Hasan Javadi · Telegram: @mr_hj369")

recent_window = df.iloc[-min(len(df), 300):]
signal = strategy.generate_latest_signal(recent_window)

col1, col2, col3, col4, col5 = st.columns(5)
if signal is not None:
    direction_fa = "خرید (LONG)" if signal.direction.value == "LONG" else "فروش (SHORT)"
    col1.metric("سیگنال فعلی", direction_fa)
    col2.metric("Entry", f"{signal.entry_price:,.2f}")
    col3.metric("Stop Loss", f"{signal.stop_loss:,.2f}")
    col4.metric("Take Profit", f"{signal.take_profit:,.2f}")
    col5.metric("R/R | اطمینان", f"{signal.risk_reward} | {signal.confidence:.0f}%")
    with st.expander("دلایل سیگنال"):
        for r in signal.reasons:
            st.write("• " + r)
else:
    st.info("در این لحظه هیچ سیگنال معتبری (بر اساس آخرین ۳۰۰ کندل و تنظیمات فعلی) یافت نشد. "
            "می‌توانید حساسیت موتور SMC را از نوار کناری افزایش دهید.")

# ---------------------------------------------------------------------- #
# چارت اصلی
# ---------------------------------------------------------------------- #
st.subheader("چارت تحلیلی")
chart_df = df.iloc[-n_bars_display:].reset_index(drop=True)

zones = []
smc_source = getattr(strategy, "smc", strategy if hasattr(strategy, "_build_context") else None)
if smc_source is not None:
    ctx = smc_source._build_context(chart_df)
    zones = ctx["order_blocks"] + ctx["fvgs"]

overlays = {
    "EMA20": chart_df.get("ema_20"), "EMA50": chart_df.get("ema_50"),
    "BB_UPPER": chart_df.get("bb_upper"), "BB_LOWER": chart_df.get("bb_lower"),
}
overlays = {k: v for k, v in overlays.items() if v is not None}
subpanels = {"RSI": chart_df["rsi"]}

fig = build_figure(chart_df, overlays=overlays, zones=zones, signal=signal, subpanels=subpanels)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------- #
# بک‌تست
# ---------------------------------------------------------------------- #
if run_backtest_btn:
    st.subheader("نتایج بک‌تست")
    with st.spinner("در حال اجرای بک‌تست..."):
        backtest_cfg = BacktestConfig(
            initial_balance=account_balance,
            risk_percent_per_trade=risk_pct,
            spread_points=config.get("backtest", {}).get("spread_points", 20),
            commission_per_lot=config.get("backtest", {}).get("commission_per_lot", 0.0),
            symbol_spec=SymbolSpec(),
            risk_config=RiskConfig(
                risk_percent_per_trade=risk_pct,
                max_daily_loss_percent=config["risk"].get("max_daily_risk_pct", 3.0),
                max_drawdown_percent=config["risk"].get("max_drawdown_pct", 10.0),
                break_even_trigger_rr=config["risk"].get("break_even_trigger_rr", 1.0),
                trailing_start_rr=1.5,
                trailing_distance_atr_mult=config["risk"].get("trailing_stop_atr_mult", 1.5),
            ),
        )

        lookback_window = 200
        check_interval = 3

        def signal_fn(window: pd.DataFrame):
            recent = window.iloc[-lookback_window:] if len(window) > lookback_window else window
            return strategy.generate_latest_signal(recent)

        engine = BacktestEngine(backtest_cfg)
        report = engine.run(df, signal_fn, atr_series=df["atr"], signal_check_interval=check_interval)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("تعداد معاملات", report.total_trades)
    m2.metric("Win Rate", f"{report.win_rate}%")
    m3.metric("Profit Factor", report.profit_factor)
    m4.metric("سود خالص", f"${report.net_profit:,.2f}")

    m5, m6, m7 = st.columns(3)
    m5.metric("Max Drawdown", f"${report.max_drawdown:,.2f} ({report.max_drawdown_percent}%)")
    m6.metric("Sharpe Ratio", report.sharpe_ratio)
    m7.metric("میانگین برد/باخت", f"${report.average_win} / ${report.average_loss}")

    if len(report.equity_curve) > 1:
        st.line_chart(report.equity_curve, use_container_width=True)
    else:
        st.warning("در این بازه‌ی داده و تنظیمات، معامله‌ای شکل نگرفت. حساسیت موتور SMC را "
                   "از نوار کناری افزایش دهید (Order Block/Swing Lookback کمتر، FVG Gap کمتر).")

st.markdown("---")
st.caption("⚠️ این نرم‌افزار صرفاً ابزار تحلیلی/آموزشی است و توصیه مالی محسوب نمی‌شود. "
           "اتصال زنده به MT5 روی این داشبورد ابری فعال نیست (فقط ویندوز). "
           "موتور هوش مصنوعی احتمال آماری بر پایه‌ی الگوهای گذشته می‌دهد، نه پیش‌بینی قطعی — جزئیات: docs/AI_MODEL.md")
