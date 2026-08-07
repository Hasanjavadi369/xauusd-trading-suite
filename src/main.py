"""
نقطه ورود اصلی XAUUSD Trading Suite.

حالت‌های اجرا:
  1) backtest : اجرای بک‌تست استراتژی SMC روی یک فایل CSV تاریخی
  2) chart    : باز کردن چارت تعاملی وب برای یک فایل CSV
  3) live     : اتصال زنده به MT5، دریافت آخرین سیگنال و (اختیاری) ارسال معامله

مثال‌ها:
    python -m src.main --mode backtest --csv data/XAUUSD_H1_real.csv
    python -m src.main --mode chart --csv data/XAUUSD_H1_real.csv
    python -m src.main --mode live --send-orders False
"""
from __future__ import annotations

import argparse

import pandas as pd
import yaml
from loguru import logger

from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.backtest.engine import BacktestEngine, BacktestConfig
from src.risk_management.position_sizing import SymbolSpec
from src.risk_management.trade_manager import RiskConfig


def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["datetime"])
    df = df.rename(columns={"datetime": "time"})
    return df.sort_values("time").reset_index(drop=True)


def load_scorer_if_enabled(config: dict):
    """اگر ml.enabled=true و فایل مدل موجود باشد، یک Scorer بارگذاری‌شده برمی‌گرداند؛ وگرنه None.

    هم فایل‌های EnsembleSignalScorer (پیش‌فرض جدید، چند مدل ترکیبی) و هم فایل‌های
    قدیمی‌تر SignalScorer (تک‌بک‌اند) را تشخیص می‌دهد.

    خطاها (مدل train نشده، فایل خراب، ...) هرگز کل اجرای backtest/live را متوقف
    نمی‌کنند — فقط هشدار می‌دهند و استراتژی بدون امتیاز ML (فقط قانون‌محور) ادامه می‌دهد.
    """
    ml_cfg = config.get("ml", {})
    if not ml_cfg.get("enabled", False):
        return None

    from pathlib import Path
    model_path = ml_cfg.get("model_path", "models/signal_scorer_ensemble.joblib")
    if not Path(model_path).exists():
        logger.warning(f"ml.enabled=true اما فایل مدل پیدا نشد: {model_path} — "
                        f"ابتدا با scripts/train_signal_model.py یک مدل train کنید. "
                        f"ادامه بدون امتیاز ML.")
        return None

    from src.ml.ensemble import EnsembleSignalScorer
    from src.ml.scorer import SignalScorer
    try:
        scorer = EnsembleSignalScorer.load(model_path)
        logger.info(f"موتور Ensemble بارگذاری شد: {model_path} ({scorer.backend_name})")
        return scorer
    except (TypeError, Exception):
        pass
    try:
        scorer = SignalScorer.load(model_path)
        logger.info(f"مدل امتیازدهی سیگنال بارگذاری شد: {model_path} (backend={scorer.backend_name})")
        return scorer
    except Exception as e:
        logger.warning(f"بارگذاری مدل ML شکست خورد ({e}) — ادامه بدون امتیاز ML.")
        return None


def run_backtest(csv_path: str, config: dict) -> None:
    df = load_csv(csv_path)
    df = compute_all_indicators(df, config)

    scorer = load_scorer_if_enabled(config)
    strategy = SMCConfluenceStrategy(config, scorer=scorer)
    df = strategy.prepare(df)
    min_probability = config.get("ml", {}).get("min_probability", 0.0) if scorer else 0.0

    risk_cfg = config.get("risk", {})
    backtest_cfg = BacktestConfig(
        initial_balance=risk_cfg.get("account_balance", 10_000),
        risk_percent_per_trade=risk_cfg.get("risk_per_trade_pct", 1.0),
        spread_points=config.get("backtest", {}).get("spread_points", 20),
        commission_per_lot=config.get("backtest", {}).get("commission_per_lot", 0.0),
        symbol_spec=SymbolSpec(),
        risk_config=RiskConfig(
            risk_percent_per_trade=risk_cfg.get("risk_per_trade_pct", 1.0),
            max_daily_loss_percent=risk_cfg.get("max_daily_risk_pct", 3.0),
            max_drawdown_percent=risk_cfg.get("max_drawdown_pct", 10.0),
            break_even_trigger_rr=risk_cfg.get("break_even_trigger_rr", 1.0),
            trailing_start_rr=1.5,
            trailing_distance_atr_mult=risk_cfg.get("trailing_stop_atr_mult", 1.5),
        ),
    )

    # برای کارایی، فقط روی یک پنجره‌ی متحرک اخیر (نه کل تاریخچه از ابتدا) تحلیل
    # ساختار بازار/SMC انجام می‌شود؛ این هم به واقعیت تحلیل زنده نزدیک‌تر است
    # (معامله‌گر معمولا به چند صد کندل اخیر نگاه می‌کند، نه کل تاریخچه)
    lookback_window = config.get("smc", {}).get("analysis_window_bars", 200)
    check_interval = config.get("backtest", {}).get("signal_check_interval", 3)

    def signal_fn(window: pd.DataFrame):
        recent = window.iloc[-lookback_window:] if len(window) > lookback_window else window
        signal = strategy.generate_latest_signal(recent)
        if signal is not None and min_probability > 0 and signal.ml_probability is not None:
            if signal.ml_probability < min_probability:
                return None
        return signal

    engine = BacktestEngine(backtest_cfg)
    report = engine.run(df, signal_fn, atr_series=df["atr"], signal_check_interval=check_interval)

    logger.info("=== نتیجه بک‌تست ===")
    for k, v in report.to_dict().items():
        logger.info(f"{k}: {v}")


def run_chart(csv_path: str, config: dict) -> None:
    from src.chart.chart_app import build_figure, run_dash_app

    df = load_csv(csv_path)
    df = compute_all_indicators(df, config)
    scorer = load_scorer_if_enabled(config)
    strategy = SMCConfluenceStrategy(config, scorer=scorer)
    df = strategy.prepare(df)
    ctx = strategy._build_context(df)

    overlays = {
        "EMA20": df["ema_20"], "EMA50": df["ema_50"],
        "BB_UPPER": df.get("bb_upper"), "BB_LOWER": df.get("bb_lower"),
    }
    overlays = {k: v for k, v in overlays.items() if v is not None}
    subpanels = {"RSI": df["rsi"], "MACD": df["macd"]}

    zones = ctx["order_blocks"] + ctx["fvgs"]
    signals = strategy.generate_signals(df)
    last_signal = signals[-1] if signals else None

    run_dash_app(df, overlays=overlays, zones=zones, signal=last_signal, subpanels=subpanels, debug=True)


def run_live(config: dict, send_orders: bool = False) -> None:
    from src.connectors.mt5_connector import MT5Connector, MT5Credentials

    mt5_cfg = config.get("mt5", {})
    creds = MT5Credentials(
        login=mt5_cfg.get("login") or None,
        password=mt5_cfg.get("password") or None,
        server=mt5_cfg.get("server") or None,
        path=mt5_cfg.get("terminal_path") or None,
    )

    with MT5Connector(creds, symbol=config.get("symbol", "XAUUSD")) as conn:
        df = conn.get_ohlcv(timeframe=config.get("timeframe", "H1"), n_bars=500)
        df = df.reset_index().rename(columns={"datetime": "time"})
        df = compute_all_indicators(df, config)

        scorer = load_scorer_if_enabled(config)
        strategy = SMCConfluenceStrategy(config, scorer=scorer)
        df = strategy.prepare(df)
        signal = strategy.generate_latest_signal(df)

        if signal is None:
            logger.info("سیگنال معتبری در این لحظه یافت نشد.")
            return

        min_probability = config.get("ml", {}).get("min_probability", 0.0)
        if scorer and min_probability > 0 and signal.ml_probability is not None \
                and signal.ml_probability < min_probability:
            logger.info(f"سیگنال یافت شد اما امتیاز مدل ({signal.ml_probability:.2f}) "
                        f"کمتر از آستانه‌ی ml.min_probability ({min_probability}) است؛ نادیده گرفته شد.")
            return

        ml_part = f" | ML={signal.ml_probability:.2f}" if signal.ml_probability is not None else ""
        logger.info(f"سیگنال جدید: {signal.direction} | Entry={signal.entry_price} "
                    f"SL={signal.stop_loss} TP={signal.take_profit} R/R={signal.risk_reward} "
                    f"Confidence={signal.confidence}{ml_part}")
        for r in signal.reasons:
            logger.info(f"  - {r}")

        if send_orders:
            from src.risk_management.position_sizing import calculate_position_size, SymbolSpec
            account = conn.get_account_info()
            balance = account["balance"] if account else config["risk"]["account_balance"]
            volume = calculate_position_size(
                account_balance=balance,
                risk_percent=config["risk"]["risk_per_trade_pct"],
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                symbol_spec=SymbolSpec(),
            )
            direction = "BUY" if signal.direction.value == "LONG" else "SELL"
            result = conn.send_market_order(direction, volume, signal.stop_loss, signal.take_profit)
            logger.info(f"نتیجه ارسال سفارش: {result}")
        else:
            logger.info("send-orders=False است؛ فقط سیگنال نمایش داده شد و معامله‌ای ارسال نشد.")


def main():
    parser = argparse.ArgumentParser(description="XAUUSD Trading Suite")
    parser.add_argument("--mode", choices=["backtest", "chart", "live"], required=True)
    parser.add_argument("--csv", help="مسیر فایل CSV برای backtest/chart")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--send-orders", type=lambda x: x.lower() == "true", default=False)
    args = parser.parse_args()

    config = load_config(args.config)

    if args.mode == "backtest":
        if not args.csv:
            raise SystemExit("برای حالت backtest باید --csv مشخص شود.")
        run_backtest(args.csv, config)
    elif args.mode == "chart":
        if not args.csv:
            raise SystemExit("برای حالت chart باید --csv مشخص شود.")
        run_chart(args.csv, config)
    elif args.mode == "live":
        run_live(config, send_orders=args.send_orders)


if __name__ == "__main__":
    main()
