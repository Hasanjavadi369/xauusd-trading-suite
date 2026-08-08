"""
XAUUSD / BTCUSD Trading Suite — focused live signal dashboard.

Only real market data is accepted. The dashboard is intentionally narrow:
LIVE PRICE -> multi-timeframe analysis -> SMC/ICT -> technical/momentum ->
AI confirmation (when a trained real-data model exists) -> score -> BUY/SELL/NO TRADE
-> Entry / SL / TP.

Both instruments (Gold / Bitcoin) reuse the same Twelve Data API key already
configured in the sidebar — no separate setup needed per symbol.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.connectors.twelvedata_connector import fetch_time_series, fetch_latest_price, TwelveDataError
from src.signal_engine.live_signal_engine import LiveSignalEngine

st.set_page_config(
    page_title="Trading Signal Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.block-container {max-width: 1200px; padding-top: 1.2rem;}
.signal {border:1px solid rgba(128,128,128,.25); border-radius:16px; padding:24px; text-align:center; margin:12px 0;}
.signal h1 {font-size:2.6rem; margin:0 0 8px 0;}
.price {font-size:2rem; font-weight:700;}
.label {font-size:.78rem; opacity:.65; text-transform:uppercase; letter-spacing:.08em;}
.value {font-size:1.35rem; font-weight:700;}
.muted {opacity:.65;}
</style>
""", unsafe_allow_html=True)

# Supported instruments — all share the same Twelve Data API key.
INSTRUMENTS = {
    "XAU/USD": {"label": "🥇 Gold (XAU/USD)", "decimals": 3},
    "BTC/USD": {"label": "₿ Bitcoin (BTC/USD)", "decimals": 2},
}

DEFAULTS = {
    "api_key": os.getenv("TWELVEDATA_API_KEY", os.getenv("TWELVE_DATA_API_KEY", "")),
    "symbol": "XAU/USD",
    "results": {},   # symbol -> result dict
    "frames_by_symbol": {},  # symbol -> {tf: df}
    "errors_by_symbol": {},  # symbol -> [str]
    "auto_refresh": True,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("Trading Signal Engine")
st.caption("Live-only • Multi-Timeframe • SMC / ICT • Technical • Momentum • AI Confirmation")

with st.sidebar:
    st.subheader("Live Data")
    st.session_state["api_key"] = st.text_input(
        "Twelve Data API Key",
        value=st.session_state["api_key"],
        type="password",
        help="The key is used only at runtime and is not written into the repository. Shared across all instruments below.",
    )
    st.session_state["auto_refresh"] = st.toggle("Auto refresh", value=st.session_state["auto_refresh"])
    refresh = st.button("Run Live Analysis", type="primary", use_container_width=True)
    st.caption("Source: Twelve Data")
    st.caption("No synthetic/demo market prices are used.")

# Instrument selector (same API key powers every instrument).
symbol = st.radio(
    "Instrument",
    options=list(INSTRUMENTS.keys()),
    format_func=lambda s: INSTRUMENTS[s]["label"],
    horizontal=True,
    key="symbol",
)
decimals = INSTRUMENTS[symbol]["decimals"]

if st.session_state["auto_refresh"]:
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=30000, key=f"live_refresh_{symbol.replace('/', '_')}")
        refresh = True
    except Exception:
        pass

need_run = refresh or symbol not in st.session_state["results"]

if need_run:
    api_key = st.session_state["api_key"].strip()
    if not api_key:
        st.warning("Enter your Twelve Data API key in the sidebar to start live analysis.")
        st.stop()

    intervals = {"M5": ("5min", 400), "M15": ("15min", 400), "H1": ("1h", 300), "H4": ("4h", 250), "D1": ("1day", 180)}
    frames = {}
    errors = []
    progress = st.progress(0)
    for i, (tf, (interval, size)) in enumerate(intervals.items(), start=1):
        try:
            frames[tf] = fetch_time_series(symbol, interval, size, api_key=api_key)
        except Exception as exc:
            errors.append(f"{tf}: {exc}")
        progress.progress(i / len(intervals))
    progress.empty()

    if not frames:
        st.error("Live market data could not be loaded.")
        for e in errors:
            st.caption(e)
        st.stop()

    try:
        live_price = fetch_latest_price(symbol, api_key=api_key)
    except Exception as exc:
        live_price = None
        errors.append(f"LIVE PRICE: {exc}")

    config = {}
    config_path = ROOT / "config" / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception:
            config = {}

    result = LiveSignalEngine(config).analyze(frames, live_price=live_price)
    st.session_state["results"][symbol] = result.to_dict()
    st.session_state["frames_by_symbol"][symbol] = frames
    st.session_state["errors_by_symbol"][symbol] = errors

result = st.session_state["results"].get(symbol)
if not result:
    st.stop()

live_price = result.get("live_price")
if live_price is not None:
    st.markdown(f'<div class="price">{symbol} LIVE &nbsp; {float(live_price):.{decimals}f}</div>', unsafe_allow_html=True)
else:
    st.warning("Live quote unavailable; analysis is based on the latest closed candle.")

status = result["status"]
confidence = float(result.get("confidence", 0))

if status == "BUY":
    title = "🟢 BUY"
elif status == "SELL":
    title = "🔴 SELL"
else:
    title = "⚪ NO TRADE"

st.markdown(f'<div class="signal"><h1>{title}</h1><div>Signal Score / Confidence: <b>{confidence:.1f}%</b></div></div>', unsafe_allow_html=True)

if status in ("BUY", "SELL"):
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="label">Entry</div><div class="value">{result["entry"]:.{decimals}f}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="label">Stop Loss</div><div class="value">{result["sl"]:.{decimals}f}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="label">Take Profit</div><div class="value">{result["tp"]:.{decimals}f}</div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="label">Risk / Reward</div><div class="value">1 : {result["rr"]:.2f}</div>', unsafe_allow_html=True)
else:
    for reason in (result.get("reasons") or []):
        st.info(reason)
    st.caption("Entry / SL / TP are intentionally hidden until a validated BUY or SELL exists.")

st.divider()
st.subheader("Analysis Layers")

layers = result.get("layers") or {}
cols = st.columns(4)
ordered = ["multi_timeframe", "structure", "liquidity", "technical", "candles", "volatility_momentum", "ai"]
for i, name in enumerate(ordered):
    if name not in layers:
        continue
    x = layers[name]
    direction = x.get("direction", "NONE")
    dlabel = "BUY" if direction == "BUY" else "SELL" if direction == "SELL" else "NEUTRAL"
    if name == "ai":
        active = x.get("active", False)
        extra = "ACTIVE" if active else "NOT ACTIVE"
        if x.get("probability") is not None:
            extra += f" • TP probability {float(x['probability'])*100:.1f}%"
    else:
        extra = dlabel
    with cols[i % 4]:
        st.metric(name.replace("_", " ").title(), f'{float(x.get("score",0)):.0f}/100', extra)

st.subheader("Decision Reasons")
for reason in result.get("reasons") or []:
    st.write("•", reason)

if result.get("ai_active"):
    st.success(f'AI confirmation active • TP probability: {float(result.get("ai_probability",0))*100:.1f}%')
else:
    st.warning("AI confirmation is not active: no trained real-data ensemble model is installed. The engine will not invent an AI score.")

if st.session_state["errors_by_symbol"].get(symbol):
    with st.expander("Live data warnings"):
        for e in st.session_state["errors_by_symbol"][symbol]:
            st.write("•", e)

with st.expander("Multi-Timeframe details"):
    mtf = layers.get("multi_timeframe", {})
    detail = {k:v for k,v in mtf.items() if k in ("M5","M15","H1","H4","D1")}
    if detail:
        st.dataframe(pd.DataFrame(detail).T, use_container_width=True)

with st.expander("Live chart"):
    frames = st.session_state["frames_by_symbol"].get(symbol, {})
    df = frames.get("M15")
    if df is not None and not df.empty:
        try:
            import plotly.graph_objects as go
            p = df.tail(250)
            fig = go.Figure(go.Candlestick(
                x=p["time"], open=p["open"], high=p["high"], low=p["low"], close=p["close"], name=symbol
            ))
            fig.update_layout(height=550, xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=10,b=10), template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.line_chart(df.set_index("time")["close"])
