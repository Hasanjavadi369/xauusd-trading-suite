import numpy as np
import pandas as pd

from src.indicators.calculator import compute_all_indicators
from src.price_action.candlestick_patterns import detect_all_patterns
from src.ml.feature_engineering import build_features, clean_features_labels, FEATURE_COLUMNS
from src.ml.labeling import triple_barrier_labels, label_distribution
from src.ml.model import MLSignalModel


def _load_config():
    import yaml
    with open("config/config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _make_df(n=400, seed=3):
    rng = np.random.default_rng(seed)
    close = 2000 + np.cumsum(rng.normal(0, 1.2, n))
    open_ = close - rng.normal(0, 0.5, n)
    high = np.maximum(open_, close) + abs(rng.normal(0.3, 0.3, n))
    low = np.minimum(open_, close) - abs(rng.normal(0.3, 0.3, n))
    time = pd.date_range("2024-01-01", periods=n, freq="h")
    df = pd.DataFrame({"time": time, "open": open_, "high": high, "low": low,
                        "close": close, "volume": rng.integers(100, 1000, n)})
    config = _load_config()
    df = compute_all_indicators(df, config)
    return detect_all_patterns(df)


def test_build_features_returns_expected_columns():
    df = _make_df()
    features = build_features(df)
    assert list(features.columns) == FEATURE_COLUMNS
    assert len(features) == len(df)


def test_triple_barrier_labels_only_valid_classes():
    df = _make_df()
    labels = triple_barrier_labels(df, df["atr"], tp_atr_mult=2.0, sl_atr_mult=1.0, max_horizon_bars=10)
    valid = labels.dropna()
    assert set(valid.unique()).issubset({-1.0, 0.0, 1.0})


def test_label_distribution_sums_close_to_100():
    df = _make_df()
    labels = triple_barrier_labels(df, df["atr"], max_horizon_bars=10)
    dist = label_distribution(labels)
    total_pct = dist["bullish_pct"] + dist["bearish_pct"] + dist["neutral_pct"]
    assert 99.0 <= total_pct <= 101.0


def test_clean_features_labels_drops_nan_rows():
    df = _make_df()
    features = build_features(df)
    labels = triple_barrier_labels(df, df["atr"], max_horizon_bars=10)
    X, y = clean_features_labels(features, labels)
    assert len(X) == len(y)
    assert not X.isna().any().any()
    assert len(X) < len(df)  # ابتدای سری (rolling/pct_change) و انتهای برچسب‌گذاری حذف می‌شوند


def test_model_train_predict_roundtrip():
    df = _make_df(n=600)
    features = build_features(df)
    labels = triple_barrier_labels(df, df["atr"], max_horizon_bars=10)
    X, y = clean_features_labels(features, labels)

    model = MLSignalModel(model_type="random_forest", n_estimators=20)
    report = model.train(X, y, test_size=0.3)

    assert 0.0 <= report.train_accuracy <= 1.0
    assert 0.0 <= report.test_accuracy <= 1.0
    assert report.n_train + report.n_test == len(X)

    proba = model.predict_proba(X.iloc[:5])
    assert set(["proba_bearish", "proba_neutral", "proba_bullish"]).issubset(proba.columns)
    row_sums = proba.sum(axis=1)
    assert all(abs(s - 1.0) < 1e-6 for s in row_sums)


def test_model_save_and_load_roundtrip(tmp_path):
    df = _make_df(n=600)
    features = build_features(df)
    labels = triple_barrier_labels(df, df["atr"], max_horizon_bars=10)
    X, y = clean_features_labels(features, labels)

    model = MLSignalModel(model_type="random_forest", n_estimators=20)
    model.train(X, y)

    save_path = str(tmp_path / "model.joblib")
    model.save(save_path)

    loaded = MLSignalModel.load(save_path)
    original_proba = model.predict_proba(X.iloc[:10])
    loaded_proba = loaded.predict_proba(X.iloc[:10])
    pd.testing.assert_frame_equal(original_proba, loaded_proba)
