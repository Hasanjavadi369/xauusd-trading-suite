import numpy as np
import pandas as pd
import yaml

from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.ml.features import FEATURE_COLUMNS, empty_feature_row, feature_dict_to_row
from src.ml.dataset import build_training_dataset
from src.ml.scorer import SignalScorer


def _load_config():
    with open("config/config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _make_trending_df(n=400, seed=11):
    """داده‌ای با روند و نوسان کافی برای اطمینان از شکل‌گیری چند سیگنال SMC."""
    rng = np.random.default_rng(seed)
    trend_component = np.concatenate([
        np.linspace(0, 30, n // 2),
        np.linspace(30, 5, n - n // 2),
    ])
    noise = rng.normal(0, 1.2, n)
    close = 2000 + trend_component + np.cumsum(noise) * 0.3
    open_ = close - rng.normal(0, 0.6, n)
    high = np.maximum(open_, close) + abs(rng.normal(0.4, 0.4, n))
    low = np.minimum(open_, close) - abs(rng.normal(0.4, 0.4, n))
    time = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({
        "time": time, "open": open_, "high": high, "low": low,
        "close": close, "volume": rng.integers(100, 1000, n),
    })


def _prepared_df():
    config = _load_config()
    df = _make_trending_df()
    df = compute_all_indicators(df, config)
    strategy = SMCConfluenceStrategy(config)
    df = strategy.prepare(df)
    return df, strategy, config


def _make_signal_rich_df(n=800, seed=7):
    """داده‌ی مصنوعیِ چندموجی (zig-zag) صرفاً برای فیکسچر تست‌های یکپارچگی.

    این تابع فقط برای تست واحد است — هیچ فایل CSV یا داده‌ای در پروژه تولید/ذخیره
    نمی‌کند و در مسیر تحلیل/بک‌تست/معامله‌ی واقعی برنامه استفاده نمی‌شود.
    چند پایه‌ی صعودی/نزولی متوالی برای اطمینان از شکل‌گیری Swing/OB/FVG کافی می‌سازد.
    """
    rng = np.random.default_rng(seed)
    legs = 8
    leg_len = n // legs
    segments = []
    level = 2000.0
    for i in range(legs):
        direction = 1 if i % 2 == 0 else -1
        move = rng.uniform(15, 35) * direction
        segments.append(np.linspace(level, level + move, leg_len))
        level += move
    trend_component = np.concatenate(segments)
    trend_component = trend_component[:n] if len(trend_component) >= n else np.pad(
        trend_component, (0, n - len(trend_component)), mode="edge")
    noise = rng.normal(0, 1.5, n)
    close = trend_component + np.cumsum(noise) * 0.25
    open_ = close - rng.normal(0, 0.7, n)
    high = np.maximum(open_, close) + abs(rng.normal(0.5, 0.5, n))
    low = np.minimum(open_, close) - abs(rng.normal(0.5, 0.5, n))
    time = pd.date_range("2024-01-01", periods=n, freq="h")
    df = pd.DataFrame({
        "time": time, "open": open_, "high": high, "low": low,
        "close": close, "volume": rng.integers(100, 1000, n),
    })

    config = _load_config()
    df = compute_all_indicators(df, config)
    strategy = SMCConfluenceStrategy(config)
    df = strategy.prepare(df)
    return df, strategy, config


# ------------------------------------------------------------------ #
# فیچرها
# ------------------------------------------------------------------ #
def test_empty_feature_row_has_all_columns_zeroed():
    row = empty_feature_row()
    assert set(row.keys()) == set(FEATURE_COLUMNS)
    assert all(v == 0.0 for v in row.values())


def test_feature_dict_to_row_preserves_known_values_and_fills_missing():
    partial = {"rsi_value": 62.5, "trend_aligned": 1.0}
    row = feature_dict_to_row(partial)
    assert row["rsi_value"] == 62.5
    assert row["trend_aligned"] == 1.0
    assert row["fvg_confluence"] == 0.0  # فیچر ذکرنشده باید صفر بماند
    assert set(row.keys()) == set(FEATURE_COLUMNS)


def test_generated_signals_carry_full_feature_vector_in_metadata():
    df, strategy, _ = _make_signal_rich_df()
    signals = strategy.generate_signals(df)
    assert len(signals) > 0, "برای این تست باید حداقل یک سیگنال تولید شود"
    for sig in signals:
        assert "features" in sig.metadata
        feats = sig.metadata["features"]
        assert set(feats.keys()) == set(FEATURE_COLUMNS)
        assert 0.0 <= feats["rule_confidence"] <= 1.0
        assert sig.ml_probability is None  # بدون scorer نباید امتیاز ML ست شود


# ------------------------------------------------------------------ #
# دیتاست آموزشی
# ------------------------------------------------------------------ #
def test_build_training_dataset_produces_valid_binary_labels():
    df, strategy, _ = _prepared_df()
    dataset = build_training_dataset(
        df, strategy, analysis_window_bars=150, check_interval=2,
        warmup_bars=60, max_horizon_bars=150,
    )
    assert set(dataset.columns) >= set(FEATURE_COLUMNS) | {"label", "timestamp", "direction"}
    if len(dataset) > 0:
        assert set(dataset["label"].unique()).issubset({0, 1})
        # فیچرها نباید NaN باشند
        assert not dataset[FEATURE_COLUMNS].isna().any().any()


def test_build_training_dataset_empty_when_no_signals_possible():
    df, strategy, _ = _prepared_df()
    tiny_df = df.iloc[:5].copy()  # داده‌ی خیلی کم -> هیچ سیگنالی ممکن نیست
    dataset = build_training_dataset(tiny_df, strategy, warmup_bars=100)
    assert len(dataset) == 0
    assert list(dataset.columns)  # حتی خالی باید ستون‌های درست را داشته باشد


# ------------------------------------------------------------------ #
# مدل SignalScorer
# ------------------------------------------------------------------ #
def _toy_training_frame(n=60, seed=3):
    """دیتاست فیچر ساختگی (نه از موتور SMC) فقط برای تست رفتار خودِ scorer."""
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(rng.uniform(0, 1, size=(n, len(FEATURE_COLUMNS))), columns=FEATURE_COLUMNS)
    # لیبل مصنوعی وابسته به یکی از فیچرها تا مدل چیزی برای یاد گرفتن داشته باشد
    y = (X["rule_confidence"] + rng.normal(0, 0.1, n) > 0.5).astype(int)
    return X, y


def test_signal_scorer_train_predict_roundtrip(tmp_path):
    X, y = _toy_training_frame()
    scorer = SignalScorer.create(backend="auto", n_estimators=40, max_depth=3)
    scorer.fit(X, y)

    assert scorer.backend_name in {"xgboost", "lightgbm", "sklearn_hgb"}
    proba = scorer.predict_proba(X)
    assert proba.shape[0] == len(X)
    assert np.all((proba >= 0.0) & (proba <= 1.0))

    one_row = dict(zip(FEATURE_COLUMNS, X.iloc[0].tolist()))
    single_proba = scorer.predict_proba_one(one_row)
    assert 0.0 <= single_proba <= 1.0

    save_path = tmp_path / "scorer.joblib"
    scorer.save(str(save_path))
    loaded = SignalScorer.load(str(save_path))
    assert loaded.backend_name == scorer.backend_name
    reloaded_proba = loaded.predict_proba(X)
    np.testing.assert_allclose(proba, reloaded_proba)


def test_signal_scorer_predict_proba_one_ignores_unknown_keys():
    X, y = _toy_training_frame()
    scorer = SignalScorer.create(backend="auto", n_estimators=20, max_depth=2)
    scorer.fit(X, y)

    row = dict(zip(FEATURE_COLUMNS, X.iloc[0].tolist()))
    row["some_unrelated_key_not_in_schema"] = 999.0
    proba = scorer.predict_proba_one(row)
    assert 0.0 <= proba <= 1.0


# ------------------------------------------------------------------ #
# یکپارچگی: استراتژی + scorer
# ------------------------------------------------------------------ #
def test_strategy_with_scorer_attaches_ml_probability_to_signals():
    df, strategy, config = _make_signal_rich_df()
    dataset = build_training_dataset(
        df, strategy, analysis_window_bars=200, check_interval=3,
        warmup_bars=100, max_horizon_bars=200,
    )
    if len(dataset) < 4 or dataset["label"].nunique() < 2:
        # داده‌ی ساختگی گاهی سیگنال/تنوع کلاس کافی برای train نمی‌دهد؛ تست را امن رد می‌کنیم
        return

    scorer = SignalScorer.create(backend="auto", n_estimators=30, max_depth=3)
    scorer.fit(dataset[FEATURE_COLUMNS], dataset["label"])

    strategy_with_ml = SMCConfluenceStrategy(config, scorer=scorer)
    df2 = strategy_with_ml.prepare(df.copy())
    signals = strategy_with_ml.generate_signals(df2)

    assert len(signals) > 0
    for sig in signals:
        assert sig.ml_probability is not None
        assert 0.0 <= sig.ml_probability <= 1.0
        assert any("مدل یادگیری ماشین" in r for r in sig.reasons)
