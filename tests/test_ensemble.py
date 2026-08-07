import numpy as np
import pandas as pd

from src.ml.features import FEATURE_COLUMNS
from src.ml.ensemble import EnsembleSignalScorer, Decision


def _toy_training_frame(n=200, seed=5):
    """دیتاست فیچر ساختگی فقط برای تست رفتار خودِ Ensemble (نه موتور SMC)."""
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(rng.uniform(0, 1, size=(n, len(FEATURE_COLUMNS))), columns=FEATURE_COLUMNS)
    y = (X["rule_confidence"] + X["trend_aligned"] * 0.3 + rng.normal(0, 0.15, n) > 0.6).astype(int)
    return X, y


def test_ensemble_creates_available_backends_only():
    scorer = EnsembleSignalScorer.create()
    assert len(scorer.members) >= 3  # حداقل مدل‌های scikit-learn (که همیشه نصب‌اند) باید بسازد
    names = {m.name for m in scorer.members}
    assert "random_forest" in names
    assert "extra_trees" in names
    assert "logistic" in names


def test_ensemble_fit_predict_and_weights_sum_to_one():
    X, y = _toy_training_frame()
    scorer = EnsembleSignalScorer.create()
    scorer.fit(X, y)

    total_weight = sum(m.weight for m in scorer.members)
    assert abs(total_weight - 1.0) < 1e-6

    proba = scorer.predict_proba(X)
    assert proba.shape[0] == len(X)
    assert np.all((proba >= 0.0) & (proba <= 1.0))
    assert "ensemble_val_auc" in scorer.train_metrics


def test_ensemble_decide_returns_full_decision_object():
    X, y = _toy_training_frame()
    scorer = EnsembleSignalScorer.create()
    scorer.fit(X, y)

    row = dict(zip(FEATURE_COLUMNS, X.iloc[0].tolist()))
    decision = scorer.decide(row)

    assert isinstance(decision, Decision)
    assert 0.0 <= decision.probability <= 1.0
    assert 0.0 <= decision.confidence <= 1.0
    assert 0.0 <= decision.agreement_score <= 1.0
    assert set(decision.per_model_probability.keys()) == {m.name for m in scorer.members}
    assert len(decision.top_reasons) > 0
    for col, contribution, text in decision.top_reasons:
        assert col in FEATURE_COLUMNS
        assert isinstance(text, str) and len(text) > 0


def test_ensemble_save_and_load_roundtrip(tmp_path):
    X, y = _toy_training_frame()
    scorer = EnsembleSignalScorer.create()
    scorer.fit(X, y)

    save_path = tmp_path / "ensemble.joblib"
    scorer.save(str(save_path))
    loaded = EnsembleSignalScorer.load(str(save_path))

    row = dict(zip(FEATURE_COLUMNS, X.iloc[0].tolist()))
    assert abs(scorer.predict_proba_one(row) - loaded.predict_proba_one(row)) < 1e-9
    assert loaded.backend_name.startswith("ensemble(")


def test_weak_models_get_near_zero_weight_when_uninformative():
    """اگر یک برچسب کاملاً تصادفی (بدون رابطه با فیچرها) باشد، وزن‌ها باید تقریبا یکنواخت/کم‌معنی بمانند
    و مدل نباید خطا بدهد (سناریوی امنیتی: داده‌ی بی‌کیفیت نباید موتور را خراب کند)."""
    rng = np.random.default_rng(1)
    X = pd.DataFrame(rng.uniform(0, 1, size=(120, len(FEATURE_COLUMNS))), columns=FEATURE_COLUMNS)
    y = pd.Series(rng.integers(0, 2, 120))

    scorer = EnsembleSignalScorer.create()
    scorer.fit(X, y)
    proba = scorer.predict_proba(X)
    assert np.all((proba >= 0.0) & (proba <= 1.0))
