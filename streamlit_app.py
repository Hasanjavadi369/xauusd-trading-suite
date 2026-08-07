"""
داشبورد وب XAUUSD Trading Suite — نسخه Streamlit (ارتقا‌یافته).

این نسخه علاوه بر تحلیل زنده و بک‌تست، شامل موارد زیر است:
  • پشتیبانی کامل دوزبانه (فارسی/انگلیسی) با دکمه تغییر زبان در نوار کناری.
  • حساب دمو داخلی (بدون نیاز به بروکر) با موجودی اولیه قابل‌تنظیم.
  • معاملات خودکار بر اساس سیگنال/امتیاز مدل هوش مصنوعی و آستانه‌ی اطمینان کاربر.
  • مدیریت ریسک و سرمایه کامل (درصد ریسک، R/R، حد ضرر روزانه، Max Drawdown).
  • داشبورد پیشرفته: معاملات باز/بسته، Win Rate، سود/زیان روزانه/هفتگی/ماهانه، Equity Curve.

اجرای محلی:
    streamlit run streamlit_app.py

نکته: بخش اتصال زنده به MT5 روی سرورهای ابری (لینوکس) کار نمی‌کند، چون
پکیج رسمی MetaTrader5 فقط روی ویندوز اجرا می‌شود. این داشبورد برای تحلیل،
بک‌تست، حساب دمو و مشاهده‌ی چارت/سیگنال روی داده‌ی تاریخی (CSV) یا Twelve Data ساخته شده است.
"""
from __future__ import annotations

import io
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import yaml

from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.backtest.engine import BacktestEngine, BacktestConfig
from src.risk_management.position_sizing import SymbolSpec, calculate_position_size
from src.risk_management.trade_manager import RiskConfig
from src.chart.chart_app import build_figure, build_equity_figure
from src.chart.lightweight_chart import render_professional_chart
from src.connectors.twelvedata_connector import fetch_time_series, TwelveDataError
from src.core.data_models import TradeDirection
from src.paper_trading import DemoAccount, AutoTradeConfig, decide_auto_entry
from src.i18n import t, current_lang, set_lang, LANGS, DEFAULT_LANG

st.set_page_config(page_title="XAUUSD Trading Suite", layout="wide", page_icon="📈")

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

DEFAULT_CONFIG_PATH = "config/config.yaml"
# تعداد کندل دریافتی از منبع آنلاین ثابت است و دیگر تنظیمی در UI برایش وجود ندارد
LIVE_FETCH_OUTPUTSIZE = 500

ZONE_KIND_GROUPS = {
    "layer_order_blocks": ["order_block_bullish", "order_block_bearish"],
    "layer_fvg": ["fvg_bullish", "fvg_bearish"],
    "layer_supply_demand": ["supply", "demand"],
    "layer_liquidity": ["liquidity_eqh", "liquidity_eql"],
    "layer_support_resistance": ["support", "resistance"],
}

# ---------------------------------------------------------------------- #
# زبان (باید قبل از هر چیز مقداردهی اولیه شود چون CSS/متن‌ها به آن وابسته‌اند)
# ---------------------------------------------------------------------- #
if "lang" not in st.session_state:
    st.session_state["lang"] = DEFAULT_LANG

_lang_keys = list(LANGS.keys())
_lang_choice = st.sidebar.radio(
    t("lang_switch_label"),
    options=_lang_keys,
    format_func=lambda k: LANGS[k]["label"],
    index=_lang_keys.index(current_lang()),
    horizontal=True,
    key="lang_radio",
)
if _lang_choice != st.session_state["lang"]:
    set_lang(_lang_choice)
    st.rerun()

_lang_meta = LANGS[current_lang()]

# ---------------------------------------------------------------------- #
# استایل سفارشی (تم تیره + طلایی، فونت مناسب هر زبان، جهت RTL/LTR پویا)
# ---------------------------------------------------------------------- #
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;800&family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"]  {{
    font-family: {_lang_meta['font']} !important;
}}

.stApp {{
    direction: {_lang_meta['dir']};
}}

.block-container {{ padding-top: 1.4rem; }}

.gts-header {{
    display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(135deg, #1a1d24 0%, #14161b 100%);
    border: 1px solid rgba(245,166,35,0.25);
    border-radius: 14px; padding: 18px 26px; margin-bottom: 14px;
}}
.gts-header h1 {{ margin: 0; font-size: 1.55rem; color: #f5f5f5; }}
.gts-header .sub {{ color: #9aa0a6; font-size: 0.85rem; margin-top: 2px; }}
.gts-price {{ text-align: {'left' if _lang_meta['dir'] == 'rtl' else 'right'}; }}
.gts-price .val {{ font-size: 1.9rem; font-weight: 800; color: #f5a623; direction: ltr; }}
.gts-price .chg {{ font-size: 0.95rem; font-weight: 600; direction: ltr; }}
.gts-price .chg.up {{ color: #26a69a; }}
.gts-price .chg.down {{ color: #ef5350; }}

.gts-card {{
    background: #14161b; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 14px 16px; text-align: center;
}}
.gts-card .label {{ color: #9aa0a6; font-size: 0.78rem; margin-bottom: 6px; }}
.gts-card .value {{ font-size: 1.25rem; font-weight: 700; color: #f0f0f0; }}
.gts-card .value.pos {{ color: #26a69a; }}
.gts-card .value.neg {{ color: #ef5350; }}

.gts-signal-long {{
    background: linear-gradient(135deg, rgba(38,166,154,0.18), rgba(38,166,154,0.04));
    border: 1px solid rgba(38,166,154,0.5); border-radius: 14px; padding: 16px 20px;
}}
.gts-signal-short {{
    background: linear-gradient(135deg, rgba(239,83,80,0.18), rgba(239,83,80,0.04));
    border: 1px solid rgba(239,83,80,0.5); border-radius: 14px; padding: 16px 20px;
}}
.gts-signal-none {{
    background: #14161b; border: 1px dashed rgba(255,255,255,0.15);
    border-radius: 14px; padding: 16px 20px; color: #9aa0a6;
}}
.gts-badge {{
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    font-weight: 700; font-size: 0.85rem;
}}
.gts-badge-long {{ background: #26a69a; color: #06231f; }}
.gts-badge-short {{ background: #ef5350; color: #2a0908; }}

.gts-status-on {{
    background: rgba(38,166,154,0.12); border: 1px solid rgba(38,166,154,0.4);
    border-radius: 10px; padding: 8px 14px; font-size: 0.85rem; color: #26a69a;
}}
.gts-status-off {{
    background: rgba(255,255,255,0.04); border: 1px dashed rgba(255,255,255,0.15);
    border-radius: 10px; padding: 8px 14px; font-size: 0.85rem; color: #9aa0a6;
}}

footer {{visibility: hidden;}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


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


# ---------------------------------------------------------------------- #
# نوار کناری: تنظیمات
# ---------------------------------------------------------------------- #
st.sidebar.title(t("sidebar_title"))

with st.sidebar.expander(t("data_source_header"), expanded=True):
    data_source = st.radio(
        t("data_source_radio_label"),
        [t("data_source_option_live"), t("data_source_option_csv")],
        index=0,
    )

    uploaded = None
    td_symbol, td_interval, td_fetch_btn = None, None, False
    auto_refresh = False

    if data_source == t("data_source_option_csv"):
        uploaded = st.file_uploader(t("csv_uploader_label"), type=["csv"])
    else:
        td_symbol = st.text_input(t("td_symbol_label"), value="XAU/USD")
        td_interval = st.selectbox(t("td_timeframe_label"), ["M15", "M30", "H1", "H4", "D1"], index=2)
        td_fetch_btn = st.button(t("td_fetch_btn"), use_container_width=True)
        auto_refresh = st.checkbox(t("auto_refresh_checkbox"), value=False)
        refresh_interval_sec = 30
        if auto_refresh:
            refresh_interval_sec = st.slider(
                t("auto_refresh_interval_label"), min_value=10, max_value=120, value=30, step=5,
            )
        with st.expander(t("api_key_guide_expander")):
            st.write(t("api_key_guide_text"))

with st.sidebar.expander(t("chart_layers_header"), expanded=False):
    visible_groups = {}
    for group_key in ZONE_KIND_GROUPS:
        visible_groups[group_key] = st.checkbox(t(group_key), value=True)
    show_rsi = st.checkbox(t("rsi_panel_checkbox"), value=True)
    show_macd = st.checkbox(t("macd_panel_checkbox"), value=False)

with st.sidebar.expander(t("risk_mgmt_header"), expanded=True):
    account_balance = st.number_input(t("account_balance_label"), value=10_000.0, step=500.0)
    risk_pct = st.slider(t("risk_pct_label"), 0.25, 5.0, 1.0, step=0.25)
    rr_target = st.slider(t("rr_target_label"), 1.0, 5.0, 2.0, step=0.5)
    max_daily_loss_pct = st.slider(t("max_daily_loss_label"), 0.5, 10.0, 3.0, step=0.5)
    max_drawdown_pct = st.slider(t("max_drawdown_label"), 5.0, 50.0, 20.0, step=1.0)
    max_open_trades = st.number_input(t("max_open_trades_label"), min_value=1, max_value=10, value=3, step=1)

with st.sidebar.expander(t("smc_sensitivity_header"), expanded=False):
    swing_lookback = st.slider(t("swing_lookback_label"), 2, 10, 5)
    order_block_lookback = st.slider(t("ob_lookback_label"), 5, 50, 20)
    fvg_min_gap_pct = st.slider(t("fvg_gap_label"), 0.0, 0.2, 0.02, step=0.01)

with st.sidebar.expander(t("ml_model_header"), expanded=False):
    st.caption(t("ml_model_caption"))
    ml_model_path = st.text_input(t("ml_model_path_label"), value="models/signal_scorer_ensemble.joblib")
    use_ml_scoring = st.checkbox(t("ml_enable_checkbox"), value=False)
    ml_min_probability = st.slider(
        t("ml_min_prob_label"), 0.0, 1.0, 0.0, step=0.05, help=t("ml_min_prob_help"),
    )
    st.divider()
    st.caption(t("cl_caption"))
    retrain_btn = st.button(t("cl_retrain_btn"), use_container_width=True)

with st.sidebar.expander(t("demo_account_header"), expanded=True):
    demo_initial_balance = st.number_input(t("demo_initial_balance_label"), value=10_000.0, step=500.0)
    reset_demo_btn = st.button(t("demo_reset_btn"), use_container_width=True)

with st.sidebar.expander(t("auto_trading_header"), expanded=True):
    auto_trading_enabled = st.checkbox(t("auto_trading_enable_checkbox"), value=False)
    auto_min_confidence = st.slider(t("auto_trading_min_conf_label"), 50.0, 99.0, 70.0, step=1.0)
    auto_prefer_ml = st.checkbox(t("auto_trading_use_ml_checkbox"), value=True)
    st.caption(t("auto_trading_hint"))

run_backtest_btn = st.sidebar.button(t("run_backtest_btn"), use_container_width=True, type="primary")

# ---------------------------------------------------------------------- #
# حساب دمو: مقداردهی اولیه / بازنشانی در session_state
# ---------------------------------------------------------------------- #
if "demo_account" not in st.session_state:
    st.session_state["demo_account"] = DemoAccount(initial_balance=demo_initial_balance, symbol="XAUUSD")

demo_account: DemoAccount = st.session_state["demo_account"]

if reset_demo_btn:
    demo_account.reset(initial_balance=demo_initial_balance)
    st.sidebar.success(t("demo_reset_success"))

# ---------------------------------------------------------------------- #
# آماده‌سازی داده و config
# ---------------------------------------------------------------------- #
config = load_config()
config["risk"]["account_balance"] = account_balance
config["risk"]["risk_per_trade_pct"] = risk_pct
config["risk"]["reward_risk_ratio"] = rr_target
config["risk"]["max_daily_risk_pct"] = max_daily_loss_pct
config["risk"]["max_drawdown_pct"] = max_drawdown_pct
config["risk"]["max_open_trades"] = max_open_trades
config["smc"]["swing_lookback"] = swing_lookback
config["smc"]["order_block_lookback"] = order_block_lookback
config["smc"]["fvg_min_gap_pct"] = fvg_min_gap_pct


def get_twelvedata_key() -> str | None:
    """کلید را ابتدا از Streamlit Secrets و سپس از متغیر محیطی می‌خواند؛ هرگز hardcode نمی‌شود."""
    try:
        if "twelvedata_api_key" in st.secrets:
            return st.secrets["twelvedata_api_key"]
    except Exception:
        pass
    return os.environ.get("TWELVEDATA_API_KEY")


connection_ok = False

if uploaded is not None:
    df_raw = load_csv_from_bytes(uploaded.read())
    st.sidebar.success(t("csv_loaded_success", n=len(df_raw)))
    connection_ok = True
else:
    if auto_refresh and HAS_AUTOREFRESH:
        st_autorefresh(interval=refresh_interval_sec * 1_000, key="gts_live_autorefresh")
    elif auto_refresh and not HAS_AUTOREFRESH:
        st.sidebar.warning(t("autorefresh_missing_warning"))

    should_fetch = td_fetch_btn or auto_refresh or ("td_data" not in st.session_state)
    if should_fetch:
        api_key = get_twelvedata_key()
        if not api_key:
            st.sidebar.error(t("td_key_missing_error"))
        else:
            try:
                with st.spinner(f"{td_symbol}..."):
                    st.session_state["td_data"] = fetch_time_series(
                        symbol=td_symbol, interval=td_interval,
                        outputsize=LIVE_FETCH_OUTPUTSIZE, api_key=api_key,
                    )
                    st.session_state["td_connected"] = True
                    st.session_state["td_last_fetch"] = datetime.now()
                if td_fetch_btn:
                    st.sidebar.success(t("td_fetched_success", n=len(st.session_state["td_data"])))
            except TwelveDataError as e:
                st.session_state["td_connected"] = False
                st.sidebar.error(t("td_error", err=e))
            except Exception as e:
                st.session_state["td_connected"] = False
                st.sidebar.error(t("td_conn_error", err=e))

    if "td_data" not in st.session_state:
        st.info(t("no_data_info"))
        st.stop()

    df_raw = st.session_state["td_data"]
    connection_ok = st.session_state.get("td_connected", False)

df = compute_all_indicators(df_raw, config)
strategy = SMCConfluenceStrategy(config)
df = strategy.prepare(df)

# ---------------------------------------------------------------------- #
# بارگذاری مدل امتیازدهی سیگنال (ML) در صورت فعال بودن
# ---------------------------------------------------------------------- #
ml_scorer = None
ml_load_error = None
if use_ml_scoring:
    from pathlib import Path as _Path
    if not _Path(ml_model_path).exists():
        ml_load_error = t("ml_not_found_error", path=ml_model_path)
    else:
        from src.ml.ensemble import EnsembleSignalScorer
        from src.ml.scorer import SignalScorer
        try:
            ml_scorer = EnsembleSignalScorer.load(ml_model_path)
            strategy.scorer = ml_scorer
        except Exception:
            try:
                ml_scorer = SignalScorer.load(ml_model_path)
                strategy.scorer = ml_scorer
            except Exception as e:
                ml_load_error = t("ml_load_failed_error", err=e)

if use_ml_scoring:
    if ml_load_error:
        st.sidebar.error(ml_load_error)
    elif ml_scorer is not None:
        st.sidebar.success(t("ml_loaded_success", backend=ml_scorer.backend_name))

# ---------------------------------------------------------------------- #
# یادگیری مستمر: ثبت نتایج واقعی معاملات (بک‌تست + دمو) و بازآموزی موتور Ensemble
# ---------------------------------------------------------------------- #
if retrain_btn:
    from src.ml.continuous_learning import (
        log_backtest_report, log_demo_account_trades, retrain_from_log,
    )
    n_logged = 0
    n_logged += log_backtest_report(st.session_state.get("last_trades", []))
    n_logged += log_demo_account_trades(demo_account.closed_trades)
    st.sidebar.info(t("cl_logged_info", n=n_logged))

    with st.spinner(t("cl_retraining_spinner")):
        result = retrain_from_log(model_output_path=ml_model_path)

    if result["status"] == "promoted":
        st.sidebar.success(t("cl_promoted_success", n=result.get("n_samples", 0),
                              auc=result.get("new_model_auc") or 0.0))
    elif result["status"] == "rejected":
        st.sidebar.warning(t("cl_rejected_warning"))
    elif result["status"] == "insufficient_data":
        st.sidebar.warning(t("cl_insufficient_data_warning", n=result.get("n_samples", 0)))
    else:
        st.sidebar.warning(result.get("message", result["status"]))

# ---------------------------------------------------------------------- #
# هدر: قیمت لحظه‌ای + عنوان
# ---------------------------------------------------------------------- #
last_row = df.iloc[-1]
prev_row = df.iloc[-2] if len(df) > 1 else last_row
price_change = last_row["close"] - prev_row["close"]
price_change_pct = (price_change / prev_row["close"] * 100) if prev_row["close"] else 0.0
chg_class = "up" if price_change >= 0 else "down"
chg_sign = "+" if price_change >= 0 else ""

_last_fetch_dt = st.session_state.get("td_last_fetch")
if uploaded is not None:
    _status_html = ""
elif _last_fetch_dt is not None and connection_ok:
    _status_html = f'<div class="sub">{t("live_status_live", ts=_last_fetch_dt.strftime("%H:%M:%S"))}</div>'
elif _last_fetch_dt is not None:
    _status_html = f'<div class="sub">{t("live_status_stale", ts=_last_fetch_dt.strftime("%H:%M:%S"))}</div>'
else:
    _status_html = ""

st.markdown(
    f"""
    <div class="gts-header">
        <div>
            <h1>{t('app_title')}</h1>
            <div class="sub">{t('app_subtitle')}</div>
            {_status_html}
        </div>
        <div class="gts-price">
            <div class="val">${last_row['close']:,.2f}</div>
            <div class="chg {chg_class}">{chg_sign}{price_change:,.2f} ({chg_sign}{price_change_pct:.2f}%)</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------- #
# محاسبه سیگنال جاری (قبل از تب‌ها چون هم برای تب زنده و هم معاملات خودکار لازم است)
# ---------------------------------------------------------------------- #
recent_window = df.iloc[-min(len(df), 300):]
signal = strategy.generate_latest_signal(recent_window)

if signal is not None and use_ml_scoring and ml_min_probability > 0 \
        and signal.ml_probability is not None and signal.ml_probability < ml_min_probability:
    signal = None  # زیر آستانه‌ی احتمال مدل -> به‌عنوان "سیگنال معتبر" نمایش داده نشود

# ---------------------------------------------------------------------- #
# به‌روزرسانی حساب دمو (Mark-to-Market) + معاملات خودکار
# ---------------------------------------------------------------------- #
current_time = last_row["time"] if isinstance(last_row["time"], datetime) else pd.Timestamp(last_row["time"]).to_pydatetime()
current_price = float(last_row["close"])

demo_account.mark_to_market(
    high=float(last_row["high"]), low=float(last_row["low"]), close=current_price, current_time=current_time,
)

daily_loss_pct = demo_account.daily_loss_percent(current_time)
halted_for_today = daily_loss_pct <= -abs(max_daily_loss_pct)

auto_cfg = AutoTradeConfig(
    enabled=auto_trading_enabled,
    min_confidence_pct=auto_min_confidence,
    prefer_ml_score=auto_prefer_ml,
    max_open_trades=int(max_open_trades),
    max_daily_loss_pct=max_daily_loss_pct,
)

should_enter = decide_auto_entry(
    signal=signal,
    cfg=auto_cfg,
    current_open_trades=len(demo_account.open_trades),
    daily_loss_pct=daily_loss_pct,
)

if should_enter and signal is not None:
    _sig_signature = (signal.timestamp, signal.direction.value, round(signal.entry_price, 2))
    if st.session_state.get("last_auto_signature") != _sig_signature:
        volume = calculate_position_size(
            account_balance=demo_account.balance,
            risk_percent=risk_pct,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            symbol_spec=SymbolSpec(),
        )
        eff_conf = (signal.ml_probability * 100.0) if (auto_prefer_ml and signal.ml_probability is not None) else signal.confidence
        demo_account.open_trade(
            direction=signal.direction,
            volume=volume,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            open_time=signal.timestamp if isinstance(signal.timestamp, datetime) else current_time,
            confidence=eff_conf,
            ml_probability=signal.ml_probability,
            features=(signal.metadata or {}).get("features"),
        )
        st.session_state["last_auto_signature"] = _sig_signature
        direction_label = t("signal_direction_long") if signal.direction == TradeDirection.LONG else t("signal_direction_short")
        st.toast(t("auto_trade_opened_toast", direction=direction_label, volume=volume, price=signal.entry_price))

tab_live, tab_backtest, tab_demo, tab_guide = st.tabs(
    [t("tab_live"), t("tab_backtest"), t("tab_demo"), t("tab_guide")]
)

# ---------------------------------------------------------------------- #
# تب ۱: تحلیل زنده
# ---------------------------------------------------------------------- #
with tab_live:
    if halted_for_today:
        st.warning(t("auto_trading_halted_warning", loss=daily_loss_pct))

    if signal is not None:
        is_long = signal.direction == TradeDirection.LONG
        css_class = "gts-signal-long" if is_long else "gts-signal-short"
        badge_class = "gts-badge-long" if is_long else "gts-badge-short"
        direction_label = t("signal_direction_long") if is_long else t("signal_direction_short")

        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if signal.ml_probability is not None:
            c0, c1, c2, c3, c4, c5 = st.columns([1.3, 1, 1, 1, 1, 1])
        else:
            c0, c1, c2, c3, c4 = st.columns([1.3, 1, 1, 1, 1])
        c0.markdown(f'<span class="gts-badge {badge_class}">{direction_label}</span>', unsafe_allow_html=True)
        c1.metric(t("signal_entry"), f"{signal.entry_price:,.2f}")
        c2.metric(t("signal_sl"), f"{signal.stop_loss:,.2f}")
        c3.metric(t("signal_tp"), f"{signal.take_profit:,.2f}")
        c4.metric(t("signal_rr_conf"), f"{signal.risk_reward} | {signal.confidence:.0f}%")
        if signal.ml_probability is not None:
            c5.metric(t("signal_ml_score"), f"{signal.ml_probability * 100:.0f}%")
        with st.expander(t("signal_reasons_expander")):
            for r in signal.reasons:
                st.write("• " + r)

        # موتور تصمیم‌گیری Ensemble: اگر مدل فعال از نوع Ensemble باشد، جزئیات
        # کامل تصمیم (Confidence Score، توافق مدل‌ها، و دلایل فیچرمحور) نمایش داده می‌شود.
        if ml_scorer is not None and hasattr(ml_scorer, "decide"):
            features = (signal.metadata or {}).get("features")
            if features:
                decision = ml_scorer.decide(features)
                with st.expander(t("ai_decision_expander"), expanded=True):
                    d1, d2, d3 = st.columns(3)
                    d1.metric(t("ai_decision_probability"), f"{decision.probability_pct():.1f}%")
                    d2.metric(t("ai_decision_confidence"), f"{decision.confidence_pct():.1f}%")
                    d3.metric(t("ai_decision_agreement"), f"{decision.agreement_score * 100:.0f}%")

                    st.caption(t("ai_decision_per_model_caption"))
                    per_model_df = pd.DataFrame([
                        {
                            t("ai_decision_model_col"): name,
                            t("ai_decision_model_weight_col"): f"{decision.per_model_weight.get(name, 0) * 100:.0f}%",
                            t("ai_decision_model_proba_col"): f"{proba * 100:.1f}%",
                        }
                        for name, proba in decision.per_model_probability.items()
                    ])
                    st.dataframe(per_model_df, use_container_width=True, hide_index=True)

                    st.caption(t("ai_decision_reasons_caption"))
                    for _col, _contribution, _text in decision.top_reasons:
                        st.write("• " + _text)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="gts-signal-none">{t("signal_none_text")}</div>', unsafe_allow_html=True)

    st.write("")

    # کارت‌های خلاصه بازار
    window24 = df.tail(24) if len(df) >= 24 else df
    k1, k2, k3, k4 = st.columns(4)
    for col, label, value in [
        (k1, t("market_card_high24"), f"{window24['high'].max():,.2f}"),
        (k2, t("market_card_low24"), f"{window24['low'].min():,.2f}"),
        (k3, t("market_card_rsi"), f"{last_row.get('rsi', float('nan')):.1f}"),
        (k4, t("market_card_atr"), f"{last_row.get('atr', float('nan')):.2f}"),
    ]:
        col.markdown(
            f'<div class="gts-card"><div class="label">{label}</div><div class="value">{value}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.subheader(t("chart_pro_header"))
    render_professional_chart(
        df,
        symbol=td_symbol.replace("/", "") if td_symbol else "XAUUSD",
        timeframe=td_interval or "H1",
        height=720,
        connection_ok=connection_ok,
    )

    st.write("")
    st.subheader(t("chart_layers_header2"))
    chart_df = df
    ctx = strategy._build_context(chart_df)
    zones = (
        ctx["order_blocks"] + ctx["fvgs"] + ctx["supply_demand"]
        + ctx["liquidity_zones"] + ctx["support_resistance"]
    )

    allowed_kinds = []
    for group_key, kinds in ZONE_KIND_GROUPS.items():
        if visible_groups.get(group_key, True):
            allowed_kinds.extend(kinds)

    overlays = {
        "EMA20": chart_df.get("ema_20"), "EMA50": chart_df.get("ema_50"),
        "BB_UPPER": chart_df.get("bb_upper"), "BB_LOWER": chart_df.get("bb_lower"),
    }
    overlays = {k: v for k, v in overlays.items() if v is not None}

    subpanels = {}
    if show_rsi and "rsi" in chart_df:
        subpanels["RSI"] = chart_df["rsi"]
    if show_macd and "macd" in chart_df:
        subpanels["MACD"] = chart_df["macd"]

    fig = build_figure(
        chart_df, overlays=overlays, zones=zones, signal=signal,
        subpanels=subpanels, zone_kinds=allowed_kinds, height=720,
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------- #
# تب ۲: بک‌تست
# ---------------------------------------------------------------------- #
with tab_backtest:
    st.subheader(t("backtest_results_header"))

    if not run_backtest_btn and "last_report" not in st.session_state:
        st.info(t("backtest_hint"))

    if run_backtest_btn:
        with st.spinner("..."):
            backtest_cfg = BacktestConfig(
                initial_balance=account_balance,
                risk_percent_per_trade=risk_pct,
                spread_points=config.get("backtest", {}).get("spread_points", 20),
                commission_per_lot=config.get("backtest", {}).get("commission_per_lot", 0.0),
                symbol_spec=SymbolSpec(),
                risk_config=RiskConfig(
                    risk_percent_per_trade=risk_pct,
                    max_daily_loss_percent=max_daily_loss_pct,
                    max_drawdown_percent=max_drawdown_pct,
                    break_even_trigger_rr=config["risk"].get("break_even_trigger_rr", 1.0),
                    trailing_start_rr=1.5,
                    trailing_distance_atr_mult=config["risk"].get("trailing_stop_atr_mult", 1.5),
                ),
            )

            lookback_window = 200
            check_interval = 3

            def signal_fn(window: pd.DataFrame):
                recent = window.iloc[-lookback_window:] if len(window) > lookback_window else window
                sig = strategy.generate_latest_signal(recent)
                if sig is not None and use_ml_scoring and ml_min_probability > 0 \
                        and sig.ml_probability is not None and sig.ml_probability < ml_min_probability:
                    return None
                return sig

            engine = BacktestEngine(backtest_cfg)
            report = engine.run(df, signal_fn, atr_series=df["atr"], signal_check_interval=check_interval)
            st.session_state["last_report"] = report
            st.session_state["last_trades"] = engine.trades

    if "last_report" in st.session_state:
        report = st.session_state["last_report"]
        trades = st.session_state.get("last_trades", [])

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric(t("metric_total_trades"), report.total_trades)
        m2.metric(t("metric_win_rate"), f"{report.win_rate}%")
        m3.metric(t("metric_profit_factor"), report.profit_factor)
        m4.metric(t("metric_net_profit"), f"${report.net_profit:,.2f}")
        m5.metric(t("metric_sharpe"), report.sharpe_ratio)

        n1, n2, n3 = st.columns(3)
        n1.metric(t("metric_max_dd"), f"${report.max_drawdown:,.2f} ({report.max_drawdown_percent}%)")
        n2.metric(t("metric_avg_win_loss"), f"${report.average_win} / ${report.average_loss}")
        n3.metric(t("metric_expectancy"), f"${report.expectancy}")

        if len(report.equity_curve) > 1:
            st.plotly_chart(
                build_equity_figure(report.equity_curve, account_balance),
                use_container_width=True,
            )

            closed = [tr for tr in trades if not tr.is_open and tr.profit is not None]
            if closed:
                trades_df = pd.DataFrame([{
                    t("col_id"): tr.id,
                    t("col_direction"): t("direction_buy") if tr.direction.value == "LONG" else t("direction_sell"),
                    t("col_open_time"): tr.open_time,
                    t("col_close_time"): tr.close_time,
                    t("col_entry"): round(tr.entry_price, 2),
                    t("col_exit"): round(tr.close_price, 2) if tr.close_price else None,
                    t("col_sl"): round(tr.stop_loss, 2),
                    t("col_tp"): round(tr.take_profit, 2),
                    t("col_volume"): tr.volume,
                    t("col_profit"): round(tr.profit, 2),
                } for tr in closed])

                st.markdown(t("trades_list_header"))
                st.dataframe(trades_df, use_container_width=True, hide_index=True)
                st.download_button(
                    t("download_trades_btn"),
                    trades_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="backtest_trades.csv",
                    mime="text/csv",
                )
        else:
            st.warning(t("backtest_no_trades_warning"))

# ---------------------------------------------------------------------- #
# تب ۳: حساب دمو (داشبورد پیشرفته)
# ---------------------------------------------------------------------- #
with tab_demo:
    st.subheader(t("demo_tab_header"))
    st.caption(t("demo_tab_caption"))

    status_class = "gts-status-on" if auto_trading_enabled else "gts-status-off"
    status_text = (
        t("demo_status_auto_on", conf=auto_min_confidence) if auto_trading_enabled else t("demo_status_auto_off")
    )
    st.markdown(f'<div class="{status_class}">{status_text}</div>', unsafe_allow_html=True)
    if halted_for_today:
        st.warning(t("auto_trading_halted_warning", loss=daily_loss_pct))

    st.write("")

    equity_now = demo_account.equity(current_price)
    floating_pnl = demo_account.floating_pnl(current_price)
    fpnl_class = "pos" if floating_pnl >= 0 else "neg"

    d1, d2, d3, d4, d5 = st.columns(5)
    for col, label, value, cls in [
        (d1, t("demo_metric_balance"), f"${demo_account.balance:,.2f}", ""),
        (d2, t("demo_metric_equity"), f"${equity_now:,.2f}", ""),
        (d3, t("demo_metric_margin"), f"${demo_account.used_margin():,.2f}", ""),
        (d4, t("demo_metric_free_margin"), f"${demo_account.free_margin(current_price):,.2f}", ""),
        (d5, t("demo_metric_floating_pnl"), f"${floating_pnl:,.2f}", fpnl_class),
    ]:
        col.markdown(
            f'<div class="gts-card"><div class="label">{label}</div>'
            f'<div class="value {cls}">{value}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    e1, e2, e3 = st.columns(3)
    e1.metric(t("demo_metric_win_rate"), f"{demo_account.win_rate()}%")
    e2.metric(t("demo_metric_total_trades"), len(demo_account.closed_trades) + len(demo_account.open_trades))
    e3.metric(t("demo_metric_max_dd"), f"{demo_account.max_drawdown_percent(current_price)}%")

    st.write("")
    st.markdown(f"**{t('demo_pnl_header')}**")
    p1, p2, p3 = st.columns(3)
    p1.metric(t("demo_pnl_today"), f"${demo_account.pnl_today(current_time):,.2f}")
    p2.metric(t("demo_pnl_week"), f"${demo_account.pnl_last_days(current_time, 7):,.2f}")
    p3.metric(t("demo_pnl_month"), f"${demo_account.pnl_last_days(current_time, 30):,.2f}")

    st.write("")
    st.markdown(f"#### {t('demo_open_positions_header')}")
    if demo_account.open_trades:
        open_rows = []
        for tr in demo_account.open_trades:
            open_rows.append({
                t("col_id"): tr.id,
                t("col_direction"): t("direction_buy") if tr.direction == TradeDirection.LONG else t("direction_sell"),
                t("col_open_time"): tr.open_time,
                t("col_entry"): round(tr.entry_price, 2),
                t("col_current_price"): round(current_price, 2),
                t("col_sl"): round(tr.stop_loss, 2),
                t("col_tp"): round(tr.take_profit, 2),
                t("col_volume"): tr.volume,
                t("col_floating_pnl"): demo_account.trade_pnl(tr, current_price),
            })
        st.dataframe(pd.DataFrame(open_rows), use_container_width=True, hide_index=True)
    else:
        st.info(t("demo_no_open_positions"))

    st.write("")
    st.markdown(f"#### {t('demo_history_header')}")
    if demo_account.closed_trades:
        closed_rows = []
        for tr in demo_account.closed_trades:
            closed_rows.append({
                t("col_id"): tr.id,
                t("col_direction"): t("direction_buy") if tr.direction == TradeDirection.LONG else t("direction_sell"),
                t("col_open_time"): tr.open_time,
                t("col_close_time"): tr.close_time,
                t("col_entry"): round(tr.entry_price, 2),
                t("col_exit"): round(tr.close_price, 2) if tr.close_price else None,
                t("col_volume"): tr.volume,
                t("col_profit"): tr.profit,
                t("col_reason"): tr.tags[-1] if tr.tags else "",
            })
        closed_df = pd.DataFrame(closed_rows)
        st.dataframe(closed_df, use_container_width=True, hide_index=True)
        st.download_button(
            t("download_trades_btn"),
            closed_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="demo_account_trades.csv",
            mime="text/csv",
        )

        st.write("")
        st.markdown(f"#### {t('demo_equity_chart_header')}")
        curve = pd.Series(demo_account.equity_curve(current_price))
        st.plotly_chart(build_equity_figure(curve, demo_account.initial_balance), use_container_width=True)
    else:
        st.info(t("demo_no_history"))

# ---------------------------------------------------------------------- #
# تب ۴: راهنما
# ---------------------------------------------------------------------- #
with tab_guide:
    st.markdown(t("guide_content"))

st.markdown("---")
st.caption(t("footer_text"))
