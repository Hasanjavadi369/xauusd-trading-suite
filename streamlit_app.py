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

import pandas as pd
import streamlit as st
import yaml

from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.backtest.engine import BacktestEngine, BacktestConfig
from src.risk_management.position_sizing import SymbolSpec
from src.risk_management.trade_manager import RiskConfig
from src.chart.chart_app import build_figure

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

uploaded = st.sidebar.file_uploader("فایل CSV سفارشی (اختیاری)", type=["csv"])
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

if uploaded is not None:
    df_raw = load_csv_from_bytes(uploaded.read())
    st.sidebar.success(f"{len(df_raw)} کندل از فایل شما بارگذاری شد.")
else:
    df_raw = load_default_sample()
    st.sidebar.info("از داده نمونه (شبیه‌سازی‌شده) استفاده می‌شود.")

df = compute_all_indicators(df_raw, config)
strategy = SMCConfluenceStrategy(config)
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
ctx = strategy._build_context(chart_df)
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
           "اتصال زنده به MT5 روی این داشبورد ابری فعال نیست (فقط ویندوز).")
