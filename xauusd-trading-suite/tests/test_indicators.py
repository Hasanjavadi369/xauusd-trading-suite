import numpy as np
import pandas as pd

from src.indicators import trend, momentum, volatility


def _make_df(n=100, seed=1):
    rng = np.random.default_rng(seed)
    close = 2000 + np.cumsum(rng.normal(0, 1, n))
    high = close + abs(rng.normal(0, 0.5, n))
    low = close - abs(rng.normal(0, 0.5, n))
    open_ = close + rng.normal(0, 0.3, n)
    time = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"time": time, "open": open_, "high": high, "low": low,
                          "close": close, "volume": rng.integers(100, 1000, n)})


def test_ema_matches_pandas_ewm():
    df = _make_df()
    result = trend.ema(df["close"], 10)
    expected = df["close"].ewm(span=10, adjust=False).mean()
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_rsi_bounds():
    df = _make_df()
    r = momentum.rsi(df["close"], 14)
    valid = r.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_atr_non_negative():
    df = _make_df()
    a = trend.atr(df, 14)
    assert (a.dropna() >= 0).all()


def test_bollinger_bands_ordering():
    df = _make_df()
    bb = volatility.bollinger_bands(df["close"], 20, 2)
    valid = bb.dropna()
    assert (valid["bb_upper"] >= valid["bb_mid"]).all()
    assert (valid["bb_mid"] >= valid["bb_lower"]).all()


def test_supertrend_direction_is_plus_or_minus_one():
    df = _make_df()
    st = trend.supertrend(df, 10, 3.0)
    assert set(st["supertrend_direction"].unique()).issubset({1, -1})


def test_macd_columns_present():
    df = _make_df()
    m = momentum.macd(df["close"])
    assert {"macd", "macd_signal", "macd_hist"}.issubset(m.columns)
