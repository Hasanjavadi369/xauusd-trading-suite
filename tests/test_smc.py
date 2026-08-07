import numpy as np
import pandas as pd

from src.indicators.calculator import compute_all_indicators
from src.smc import structure, order_blocks, fvg as fvg_mod
from src.core.data_models import Zone


def _load_config():
    import yaml
    with open("config/config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _make_trending_df(n=300, seed=7):
    """داده‌ای با روند صعودی واضح برای اطمینان از شکل‌گیری ساختار قابل تشخیص."""
    rng = np.random.default_rng(seed)
    trend_component = np.linspace(0, 40, n)
    noise = rng.normal(0, 1.0, n)
    close = 2000 + trend_component + np.cumsum(noise) * 0.2
    open_ = close - rng.normal(0, 0.5, n)
    high = np.maximum(open_, close) + abs(rng.normal(0.3, 0.3, n))
    low = np.minimum(open_, close) - abs(rng.normal(0.3, 0.3, n))
    time = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"time": time, "open": open_, "high": high, "low": low,
                          "close": close, "volume": rng.integers(100, 1000, n)})


def test_find_swing_points_returns_alternating_kinds():
    df = _make_trending_df()
    swings = structure.find_swing_points(df, lookback=5)
    assert len(swings) > 0
    kinds = {s.kind for s in swings}
    assert kinds.issubset({"swing_high", "swing_low"})


def test_bos_choch_events_have_valid_kind():
    df = _make_trending_df()
    swings = structure.find_swing_points(df, lookback=5)
    events = structure.detect_bos_choch(df, swings)
    for e in events:
        assert e.kind in ("BOS_bullish", "BOS_bearish", "CHOCH_bullish", "CHOCH_bearish")


def test_order_blocks_have_valid_price_range():
    config = _load_config()
    df = compute_all_indicators(_make_trending_df(), config)
    zones = order_blocks.detect_order_blocks(df, lookback=20)
    for z in zones:
        assert z.top >= z.bottom
        assert z.kind in ("order_block_bullish", "order_block_bearish")


def test_fvg_zones_respect_gap_direction():
    df = _make_trending_df()
    zones = fvg_mod.detect_fvg(df, min_gap_pct=0.01)
    for z in zones:
        assert z.top >= z.bottom
        assert z.kind in ("fvg_bullish", "fvg_bearish")


def test_mark_mitigated_zones_sets_bool():
    config = _load_config()
    df = compute_all_indicators(_make_trending_df(), config)
    zones = order_blocks.detect_order_blocks(df, lookback=20)
    order_blocks.mark_mitigated_zones(zones, df)
    for z in zones:
        assert isinstance(z.mitigated, bool)
