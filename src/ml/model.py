"""
پوشش (wrapper) مدل یادگیری ماشین برای پیش‌بینی رفتار قیمت.

مدل پیش‌فرض: GradientBoostingClassifier (یا RandomForestClassifier) از scikit-learn،
که روی ویژگی‌های `feature_engineering.build_features` و برچسب‌های
`labeling.triple_barrier_labels` آموزش می‌بیند.

طراحی طوری است که در آینده به‌سادگی بتوان مدل‌های دیگر (XGBoost، LightGBM، یا
شبکه‌های عصبی) را جایگزین کرد، بدون تغییر در بقیه‌ی پروژه — فقط این فایل عوض شود.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


@dataclass
class TrainReport:
    train_accuracy: float
    test_accuracy: float
    n_train: int
    n_test: int
    class_distribution: dict
    classification_report_text: str
    feature_importances: dict = field(default_factory=dict)


class MLSignalModel:
    """مدل طبقه‌بندی سه‌کلاسه: -1 (نزولی) / 0 (خنثی) / 1 (صعودی)."""

    def __init__(self, model_type: str = "gradient_boosting", **model_kwargs):
        self.model_type = model_type
        self.model_kwargs = model_kwargs
        self.model = self._build_estimator()
        self.feature_names_: Optional[list] = None
        self.is_trained: bool = False

    def _build_estimator(self):
        if self.model_type == "random_forest":
            defaults = dict(n_estimators=300, max_depth=6, min_samples_leaf=20,
                             class_weight="balanced_subsample", random_state=42)
            defaults.update(self.model_kwargs)
            return RandomForestClassifier(**defaults)
        defaults = dict(n_estimators=200, max_depth=3, learning_rate=0.05,
                        subsample=0.8, random_state=42)
        defaults.update(self.model_kwargs)
        return GradientBoostingClassifier(**defaults)

    def train(self, features: pd.DataFrame, labels: pd.Series,
              test_size: float = 0.2) -> TrainReport:
        """
        تقسیم زمانی (نه تصادفی) برای جلوگیری از نشت اطلاعات آینده به گذشته:
        بخش ابتدایی داده برای train، بخش انتهایی (جدیدتر) برای test.
        """
        if len(features) != len(labels):
            raise ValueError("طول ویژگی‌ها و برچسب‌ها باید برابر باشد")

        n = len(features)
        split_idx = int(n * (1 - test_size))
        X_train, X_test = features.iloc[:split_idx], features.iloc[split_idx:]
        y_train, y_test = labels.iloc[:split_idx], labels.iloc[split_idx:]

        self.feature_names_ = list(features.columns)
        self.model.fit(X_train, y_train)
        self.is_trained = True

        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)

        importances = {}
        if hasattr(self.model, "feature_importances_"):
            importances = dict(zip(self.feature_names_,
                                    [round(float(v), 4) for v in self.model.feature_importances_]))

        return TrainReport(
            train_accuracy=round(accuracy_score(y_train, train_pred), 4),
            test_accuracy=round(accuracy_score(y_test, test_pred), 4),
            n_train=len(X_train), n_test=len(X_test),
            class_distribution=y_train.value_counts(normalize=True).round(3).to_dict(),
            classification_report_text=classification_report(y_test, test_pred, zero_division=0),
            feature_importances=dict(sorted(importances.items(), key=lambda x: -x[1])),
        )

    def predict_proba(self, features: pd.DataFrame) -> pd.DataFrame:
        """خروجی: دیتافریم با ستون‌های proba_bearish, proba_neutral, proba_bullish."""
        if not self.is_trained:
            raise RuntimeError("مدل هنوز آموزش ندیده است؛ ابتدا train() یا load() را فراخوانی کنید")

        proba = self.model.predict_proba(features[self.feature_names_])
        classes = list(self.model.classes_)
        col_map = {-1.0: "proba_bearish", 0.0: "proba_neutral", 1.0: "proba_bullish"}

        result = pd.DataFrame(index=features.index)
        for i, cls in enumerate(classes):
            result[col_map.get(cls, f"proba_{cls}")] = proba[:, i]
        for col in ["proba_bearish", "proba_neutral", "proba_bullish"]:
            if col not in result.columns:
                result[col] = 0.0
        return result

    def save(self, path: str) -> None:
        if not self.is_trained:
            raise RuntimeError("مدل آموزش‌ندیده را نمی‌توان ذخیره کرد")
        payload = {
            "model": self.model,
            "model_type": self.model_type,
            "feature_names": self.feature_names_,
        }
        joblib.dump(payload, path)

    @classmethod
    def load(cls, path: str) -> "MLSignalModel":
        payload = joblib.load(path)
        instance = cls(model_type=payload["model_type"])
        instance.model = payload["model"]
        instance.feature_names_ = payload["feature_names"]
        instance.is_trained = True
        return instance

    def save_report(self, report: TrainReport, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "train_accuracy": report.train_accuracy,
                "test_accuracy": report.test_accuracy,
                "n_train": report.n_train,
                "n_test": report.n_test,
                "class_distribution": report.class_distribution,
                "feature_importances": report.feature_importances,
            }, f, ensure_ascii=False, indent=2)
