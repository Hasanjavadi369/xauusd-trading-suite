"""
مدل امتیازدهی سیگنال (Signal Scoring Model) — نه پیش‌بینی قیمت.

این ماژول یک classifier یاد می‌گیرد که ورودی‌اش دقیقاً همان فیچرهای قابل‌مشاهده‌ی
موتور SMC/اندیکاتور است (src/ml/features.py) و خروجی‌اش احتمال این است که یک
سیگنال مشخص، قبل از خوردن Stop Loss به Take Profit برسد. یعنی:

  * مدل قیمت آینده را حدس نمی‌زند (این کار regression روی قیمت خام است که به‌شدت
    مستعد overfitting و گمراه‌کننده است).
  * مدل فقط یاد می‌گیرد که «از بین سیگنال‌های تاریخی، کدام ترکیب از فیچرها بیشتر
    منجر به برد شده». این کاملاً روی داده‌ی موجود پروژه (خروجی SMCConfluenceStrategy)
    قابل train است و هیچ داده‌ی بیرونی/جعبه‌سیاه لازم ندارد.
  * چون فیچرها از پیش تعریف و مستندند (features.py) و می‌توان feature_importance
    را بعد از train چاپ کرد، مدل تفسیرپذیر باقی می‌ماند.

بک‌اند مدل به ترتیب اولویت انتخاب می‌شود: XGBoost > LightGBM > (اگر هیچ‌کدام نصب
نبود) HistGradientBoostingClassifier از scikit-learn به‌عنوان جایگزین سبک — طوری
که پروژه بدون نصب اجباری کتابخانه‌ی سنگین هم قابل اجرا/تست باشد.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from .features import FEATURE_COLUMNS, feature_dict_to_row


def _make_backend(backend: str, random_state: int = 42, **kwargs):
    """سعی می‌کند بک‌اند خواسته‌شده را بسازد؛ در غیر این صورت به بعدی سقوط می‌کند."""
    if backend == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", 4),
            learning_rate=kwargs.get("learning_rate", 0.05),
            subsample=kwargs.get("subsample", 0.8),
            colsample_bytree=kwargs.get("colsample_bytree", 0.8),
            reg_lambda=kwargs.get("reg_lambda", 1.0),
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=-1,
        ), "xgboost"
    if backend == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", 4),
            learning_rate=kwargs.get("learning_rate", 0.05),
            subsample=kwargs.get("subsample", 0.8),
            colsample_bytree=kwargs.get("colsample_bytree", 0.8),
            random_state=random_state,
            n_jobs=-1,
            verbose=-1,
        ), "lightgbm"
    if backend == "sklearn":
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(
            max_depth=kwargs.get("max_depth", 4),
            learning_rate=kwargs.get("learning_rate", 0.05),
            max_iter=kwargs.get("n_estimators", 300),
            random_state=random_state,
        ), "sklearn_hgb"
    raise ValueError(f"بک‌اند ناشناخته: {backend}")


def _auto_backend(preferred: Optional[List[str]] = None, **kwargs):
    """اولین بک‌اند نصب‌شده از لیست ترجیحات را برمی‌گرداند؛ سقوط نهایی: sklearn (همیشه موجود است)."""
    order = preferred or ["xgboost", "lightgbm", "sklearn"]
    last_err = None
    for name in order:
        try:
            return _make_backend(name, **kwargs)
        except ImportError as e:
            last_err = e
            continue
    # sklearn باید همیشه کار کند؛ اگر حتی آن هم نبود خطای اصلی را بالا بده
    raise RuntimeError(f"هیچ بک‌اند مدلی در دسترس نیست: {last_err}")


@dataclass
class SignalScorer:
    """Wrapper نازک روی یک classifier درخت‌محور برای امتیازدهی سیگنال‌های SMC."""

    model: object = None
    backend_name: str = "unfit"
    feature_columns: List[str] = field(default_factory=lambda: list(FEATURE_COLUMNS))
    trained_at: Optional[str] = None
    train_metrics: Dict[str, float] = field(default_factory=dict)
    feature_importance_: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def create(cls, backend: str = "auto", **model_kwargs) -> "SignalScorer":
        if backend == "auto":
            model, backend_name = _auto_backend(**model_kwargs)
        else:
            model, backend_name = _make_backend(backend, **model_kwargs)
        return cls(model=model, backend_name=backend_name)

    # ------------------------------------------------------------------ #
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "SignalScorer":
        X = X[self.feature_columns]
        self.model.fit(X, y)

        import datetime as _dt
        self.trained_at = _dt.datetime.now(_dt.UTC).isoformat()

        importances = getattr(self.model, "feature_importances_", None)
        if importances is None:
            # HistGradientBoostingClassifier (بک‌اند سقوط sklearn) اهمیت فیچر بومی
            # ندارد؛ به‌جایش permutation importance روی همان داده‌ی آموزش محاسبه می‌شود
            # (فقط برای گزارش تفسیرپذیری، نه برای انتخاب مدل).
            try:
                from sklearn.inspection import permutation_importance
                result = permutation_importance(self.model, X, y, n_repeats=5, random_state=0, n_jobs=-1)
                importances = result.importances_mean
            except Exception:
                importances = None

        if importances is not None:
            self.feature_importance_ = dict(
                sorted(zip(self.feature_columns, [float(v) for v in importances]),
                       key=lambda kv: kv[1], reverse=True)
            )
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """احتمال برد (کلاس ۱) را برای چند ردیف برمی‌گرداند."""
        X = X[self.feature_columns]
        proba = self.model.predict_proba(X)
        return proba[:, 1]

    def predict_proba_one(self, feature_row: Dict[str, float]) -> float:
        """احتمال برد برای یک سیگنال منفرد (دیکشنری فیچر) — برای استفاده در حالت زنده/بک‌تست."""
        row = feature_dict_to_row(feature_row)
        X = pd.DataFrame([row])[self.feature_columns]
        return float(self.model.predict_proba(X)[0, 1])

    # ------------------------------------------------------------------ #
    def save(self, path: str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str) -> "SignalScorer":
        obj = joblib.load(Path(path))
        if not isinstance(obj, cls):
            raise TypeError(f"فایل {path} یک SignalScorer معتبر نیست.")
        return obj

    def summary(self) -> str:
        lines = [
            f"بک‌اند مدل: {self.backend_name}",
            f"تاریخ آموزش (UTC): {self.trained_at}",
            f"معیارهای ارزیابی: {self.train_metrics}",
            "اهمیت فیچرها (نزولی):",
        ]
        for k, v in self.feature_importance_.items():
            lines.append(f"  - {k}: {v:.4f}")
        return "\n".join(lines)
