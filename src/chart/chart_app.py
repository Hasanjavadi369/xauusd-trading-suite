"""
چارت تعاملی وب (شبیه TradingView) با Plotly + Dash.

نمایش می‌دهد:
  - کندل‌استیک اصلی + حجم
  - لایه‌های تحلیلی: Order Blocks، FVG، Supply/Demand، خطوط ساختار (BOS/CHOCH)
  - اندیکاتورهای همپوشان (EMA/SMA/Bollinger/SuperTrend/Ichimoku) روی چارت اصلی
  - اندیکاتورهای زیرچارت (RSI/MACD/ADX) در پنل‌های جدا
  - نشانگر Entry/SL/TP برای سیگنال فعلی

اجرا:
    python -m src.chart.chart_app --csv data/XAUUSD_H1_real.csv
"""
from __future__ import annotations

import argparse

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from plotly.subplots import make_subplots

from src.core.data_models import Signal, Zone


def build_figure(
    df: pd.DataFrame,
    overlays: dict | None = None,
    zones: list[Zone] | None = None,
    signal: Signal | None = None,
    subpanels: dict | None = None,
    zone_kinds: list[str] | None = None,
    height: int = 780,
) -> go.Figure:
    """
    df: OHLCV با ایندکس datetime
    overlays: {"EMA20": pd.Series, "SMA50": pd.Series, ...} -> روی چارت اصلی رسم می‌شود
    zones: لیست Zone (Order Block / FVG / Supply-Demand / Liquidity / S-R) برای رسم مستطیل‌های رنگی
    signal: سیگنال فعلی برای نمایش خطوط Entry/SL/TP
    subpanels: {"RSI": pd.Series, "MACD": pd.Series, ...} -> هرکدام یک ردیف جدا
    zone_kinds: اگر مشخص شود، فقط ناحیه‌هایی با این kind رسم می‌شوند (فیلتر نمایش)
    """
    overlays = overlays or {}
    zones = zones or []
    subpanels = subpanels or {}
    if zone_kinds is not None:
        zones = [z for z in zones if z.kind in zone_kinds]

    # این ماژول برای رسم به یک DatetimeIndex نیاز دارد؛ اگر df ستون 'time' دارد
    # (قرارداد بقیه پروژه: RangeIndex + ستون time)، آن را موقتاً ایندکس می‌کنیم.
    if "time" in df.columns:
        df = df.set_index(pd.to_datetime(df["time"]))

    n_sub = len(subpanels)
    row_heights = [0.55, 0.15] + [0.3 / max(n_sub, 1)] * n_sub if n_sub else [0.7, 0.3]
    rows = 2 + n_sub

    fig = make_subplots(
        rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.02,
        row_heights=row_heights,
        specs=[[{"secondary_y": False}]] * rows,
    )

    # --- کندل‌استیک اصلی ---
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"],
            name="XAUUSD", increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
        ),
        row=1, col=1,
    )

    # --- اندیکاتورهای همپوشان ---
    palette = ["#f5a623", "#7b61ff", "#00bcd4", "#ff4081", "#8bc34a"]
    for i, (name, series) in enumerate(overlays.items()):
        fig.add_trace(
            go.Scatter(x=df.index, y=series, name=name, line=dict(width=1.3, color=palette[i % len(palette)])),
            row=1, col=1,
        )

    # --- ناحیه‌های SMC (Order Block / FVG / Supply-Demand / Liquidity / S-R) ---
    zone_colors = {
        "order_block_bullish": "rgba(38,166,154,0.28)",
        "order_block_bearish": "rgba(239,83,80,0.28)",
        "fvg_bullish": "rgba(0,188,212,0.20)",
        "fvg_bearish": "rgba(255,64,129,0.20)",
        "supply": "rgba(239,83,80,0.15)",
        "demand": "rgba(38,166,154,0.15)",
        "liquidity_eqh": "rgba(245,166,35,0.18)",
        "liquidity_eql": "rgba(123,97,255,0.18)",
        "support": "rgba(38,166,154,0.12)",
        "resistance": "rgba(239,83,80,0.12)",
    }
    zone_labels = {
        "order_block_bullish": "Order Block صعودی",
        "order_block_bearish": "Order Block نزولی",
        "fvg_bullish": "FVG صعودی",
        "fvg_bearish": "FVG نزولی",
        "supply": "ناحیه عرضه (Supply)",
        "demand": "ناحیه تقاضا (Demand)",
        "liquidity_eqh": "نقدینگی سقف‌های برابر (EQH)",
        "liquidity_eql": "نقدینگی کف‌های برابر (EQL)",
        "support": "حمایت",
        "resistance": "مقاومت",
    }
    kinds_present = []
    for zone in zones:
        color = zone_colors.get(zone.kind, "rgba(150,150,150,0.15)")
        end_time = zone.end_time or df.index[-1]
        fig.add_shape(
            type="rect", xref="x", yref="y",
            x0=zone.start_time, x1=end_time, y0=zone.bottom, y1=zone.top,
            fillcolor=color, line=dict(width=0), row=1, col=1,
        )
        if zone.kind not in kinds_present:
            kinds_present.append(zone.kind)

    # ردهای نامرئی فقط برای نمایش لجند رنگ هر نوع ناحیه (چون add_shape خودش در لجند دیده نمی‌شود)
    import re as _re
    for kind in kinds_present:
        raw = zone_colors.get(kind, "rgba(150,150,150,0.15)")
        solid_color = _re.sub(r",\s*[\d.]+\)$", ",1.0)", raw)
        fig.add_trace(
            go.Scatter(
                x=[df.index[0]], y=[None], mode="markers",
                marker=dict(size=10, color=solid_color, symbol="square"),
                name=zone_labels.get(kind, kind), showlegend=True,
            ),
            row=1, col=1,
        )

    # --- سیگنال فعلی: Entry / SL / TP ---
    if signal is not None:
        for price, label, color in [
            (signal.entry_price, "Entry", "#ffffff"),
            (signal.stop_loss, "SL", "#ef5350"),
            (signal.take_profit, "TP", "#26a69a"),
        ]:
            fig.add_hline(y=price, line_dash="dot", line_color=color,
                          annotation_text=f"{label} {price:.2f}", annotation_position="right",
                          row=1, col=1)

    # --- حجم ---
    volume_colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    fig.add_trace(go.Bar(x=df.index, y=df["volume"], marker_color=volume_colors, name="حجم"), row=2, col=1)

    # --- پنل‌های زیرچارت (RSI, MACD, ADX, ...) ---
    for i, (name, series) in enumerate(subpanels.items()):
        r = 3 + i
        fig.add_trace(go.Scatter(x=df.index, y=series, name=name, line=dict(width=1.2)), row=r, col=1)
        if name.upper() == "RSI":
            fig.add_hline(y=70, line_dash="dash", line_color="gray", row=r, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="gray", row=r, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(family="Vazirmatn, Tahoma, sans-serif", color="#e6e6e6"),
        margin=dict(l=40, r=40, t=40, b=20),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.06, x=0, bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    return fig


def build_equity_figure(equity_curve: pd.Series, initial_balance: float) -> go.Figure:
    """نمودار Equity Curve + Drawdown زیر آن، برای نمایش نتیجه بک‌تست."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04,
        row_heights=[0.7, 0.3],
    )

    fig.add_trace(
        go.Scatter(
            x=list(range(len(equity_curve))), y=equity_curve.values,
            mode="lines", name="Equity", line=dict(color="#f5a623", width=2),
            fill="tozeroy", fillcolor="rgba(245,166,35,0.08)",
        ),
        row=1, col=1,
    )
    fig.add_hline(y=initial_balance, line_dash="dash", line_color="#888",
                  annotation_text="موجودی اولیه", row=1, col=1)

    running_max = equity_curve.cummax()
    drawdown_pct = (equity_curve - running_max) / running_max * 100
    fig.add_trace(
        go.Scatter(
            x=list(range(len(drawdown_pct))), y=drawdown_pct.values,
            mode="lines", name="Drawdown %", line=dict(color="#ef5350", width=1.5),
            fill="tozeroy", fillcolor="rgba(239,83,80,0.15)",
        ),
        row=2, col=1,
    )

    fig.update_layout(
        template="plotly_dark",
        height=420,
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        margin=dict(l=40, r=20, t=20, b=20),
        showlegend=False,
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Equity ($)", row=1, col=1, gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1, gridcolor="rgba(255,255,255,0.06)")
    fig.update_xaxes(title_text="شماره معامله", row=2, col=1, gridcolor="rgba(255,255,255,0.06)")
    return fig


def run_dash_app(df: pd.DataFrame, overlays=None, zones=None, signal=None, subpanels=None, debug=False):
    app = Dash(__name__)
    fig = build_figure(df, overlays, zones, signal, subpanels)
    app.layout = html.Div(
        style={"backgroundColor": "#111", "padding": "10px"},
        children=[dcc.Graph(figure=fig, style={"height": "90vh"})],
    )
    app.run(debug=debug)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="اجرای چارت تعاملی XAUUSD")
    parser.add_argument("--csv", required=True, help="مسیر فایل CSV با ستون‌های datetime,open,high,low,close,volume")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    data = pd.read_csv(args.csv, parse_dates=["datetime"])
    data = data.rename(columns={"datetime": "time"})
    run_dash_app(data, debug=args.debug)
