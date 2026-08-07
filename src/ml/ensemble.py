"""
موتور تصمیم‌گیری هوش مصنوعی (AI Decision Engine) — نسخه‌ی Ensemble.

برخلاف ``src/ml/scorer.py`` (که فقط یک بک‌اند تک‌مدلی انتخاب می‌کند)، این ماژول
چند مدل یادگیری ماشین مستقل را هم‌زمان آموزش می‌دهد، خروجی همه را با وزن‌دهی
مبتنی بر عملکرد ترکیب می‌کند و علاوه بر احتمال نهایی، یک Confidence Score و
یک توضیح قابل‌فهم (کدام فیچرها و چقدر روی این تصمیم اثر گذاشتند) تولید می‌کند.

مدل‌های عضو (بدون نیاز به GPU، سریع و پایدار):
  * XGBoost              (اگر نصب باشد)
  * LightGBM             (اگر نصب باشد)
  * Random Forest        (scikit-learn — همیشه در دسترس)
  * Extra Trees          (scikit-learn — همیشه در دسترس)
  * Logistic Regression  (scikit-learn — مدل خطی، برای تنوع در ترکیب)

هیچ داده‌ی ساختگی/فرضی در این ماژول تولید یا استفاده نمی‌شود؛ ورودی آموزش
همیشه از ``build_training_dataset`` روی داده‌ی واقعی (CSV واقعی یا API زنده)
می‌آید.

اصول طراحی:
  1) هیچ مدلی «قیمت آینده» را پیش‌بینی نمی‌کند — دقیقاً مثل SignalScorer، هر
     مدل فقط احتمال برد یک سیگنال (طبق همان فیچرهای مستند در features.py) را
     یاد می‌گیرد.
  2) وزن هر مدل در ترکیب نهایی از روی AUC آن مدل روی یک برش زمانی نگه‌داشته‌شده
     (Time-based holdout — نه تصادفی، چون داده‌ی مالی سری زمانی است) محاسبه
     می‌شود؛ مدل‌های ضعیف‌تر خودکار وزن کمتری می‌گیرند.
  3) Confidence Score ترکیبی از دو چیز است:
       - فاصله‌ی احتمال نهایی از ۰.۵ (قطعیت خودِ تصمیم)
       - میزان توافق مدل‌ها با هم (انحراف‌معیار کم بین مدل‌ها = اطمینان بیشتر)
  4) توضیح‌پذیری: چون مدل‌ها روی فیچرهای از‌پیش‌تعریف‌شده و قابل‌فهم کار
     می‌کنند (نه پیکسل خام یا متن)، سهم هر فیچر با ترکیب اهمیت مدل (feature
     importance) و انحراف مقدار آن فیچر از میانگین داده‌ی آموزش تخمین زده
     می‌شود؛ این یک تقریب سریع و بدون وابستگی سنگین است (نه SHAP دقیق)، اما
     برای توضیح «چرا» کاملاً کاربردی است.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

from .features import FEATURE_COLUMNS, feature_dict_to_row

# نام‌های قابل‌فهم فارسی برای هر فیچر — فقط برای متن توضیح، منطق مدل را تغییر نمی‌دهد.
FEATURE_LABELS_FA: Dict[str, str] = {
    "ob_strength": "قدرت ایمپالسی Order Block",
    "ob_width_atr": "عرض Order Block نسبت به ATR",
    "trend_aligned": "هم‌جهتی با روند غالب (BOS/CHOCH)",
    "fvg_confluence": "همپوشانی با Fair Value Gap",
    "fvg_strength": "قدرت شکاف FVG",
    "candle_confirmation": "تایید الگوی کندلی",
    "rsi_value": "مقدار RSI",
    "rsi_confirmation": "تایید ناحیه RSI",
    "supertrend_aligned": "هم‌جهتی SuperTrend",
    "adx_value": "قدرت روند (ADX)",
    "macd_hist": "هیستوگرام MACD",
    "bb_position": "موقعیت در باند بولینگر",
    "atr_pct": "نوسان نرمال‌شده (ATR%)",
    "liquidity_sweep_nearby": "Liquidity Sweep نزدیک",
    "sr_confluence": "همپوشانی با حمایت/مقاومت",
    "n_confluences": "تعداد دلایل تاییدکننده",
    "risk_reward": "نسبت ریسک به ریوارد",
    "rule_confidence": "اطمینان قانون‌محور موتور SMC",
}

DEFAULT_BACKENDS = ["xgboost", "lightgbm", "random_forest", "extra_trees", "logistic"]


def _make_member(name: str, random_state: int = 42, **kwargs):
    """یک مدل عضو را می‌سازد؛ اگر کتابخانه‌اش نصب نباشد ImportError می‌دهد (بالادست نادیده گرفته می‌شود)."""
    if name == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", 4),
            learning_rate=kwargs.get("learning_rate", 0.05),
            subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
            eval_metric="logloss", random_state=random_state, n_jobs=-1,
        )
    if name == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", 4),
            learning_rate=kwargs.get("learning_rate", 0.05),
            subsample=0.8, colsample_bytree=0.8,
            random_state=random_state, n_jobs=-1, verbose=-1,
        )
    if name == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", 6),
            min_samples_leaf=3, random_state=random_state, n_jobs=-1,
        )
    if name == "extra_trees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", 6),
            min_samples_leaf=3, random_state=random_state, n_jobs=-1,
        )
    if name == "logistic":
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        return make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, C=kwargs.get("C", 1.0), random_state=random_state),
        )
    raise ValueError(f"مدل عضو ناشناخته: {name}")


def _model_feature_importance(model, feature_columns: List[str]) -> Optional[Dict[str, float]]:
    """اهمیت فیچر یک مدل عضو را (اگر پشتیبانی می‌کند) استخراج می‌کند."""
    importances = getattr(model, "feature_importances_", None)
    if importances is not None:
        return dict(zip(feature_columns, [float(v) for v in importances]))
    # لجستیک: قدرمطلق ضریب‌های استانداردشده به‌عنوان اهمیت
    try:
        coefs = model.named_steps["logisticregression"].coef_[0]
        return dict(zip(feature_columns, [float(abs(c)) for c in coefs]))
    except Exception:
        return None


@dataclass
class _Member:
    name: str
    model: object
    weight: float = 0.0
    val_auc: float = 0.5
    feature_importance: Dict[str, float] = field(default_factory=dict)


@dataclass
class EnsembleSignalScorer:
    """موتور تصمیم‌گیری Ensemble — جایگزین کامل SignalScorer با خروجی غنی‌تر."""

    members: List[_Member] = field(default_factory=list)
    feature_columns: List[str] = field(default_factory=lambda: list(FEATURE_COLUMNS))
    feature_means_: Dict[str, float] = field(default_factory=dict)
    feature_stds_: Dict[str, float] = field(default_factory=dict)
    trained_at: Optional[str] = None
    train_metrics: Dict[str, float] = field(default_factory=dict)
    n_train_samples: int = 0

    # سازگاری با رابط قدیمی SignalScorer (کدهای مصرف‌کننده فقط به این‌ها نیاز دارند)
    @property
    def backend_name(self) -> str:
        if not self.members:
            return "ensemble(unfit)"
        parts = [f"{m.name}×{m.weight:.2f}" for m in self.members]
        return "ensemble(" + "+".join(parts) + ")"

    @property
    def feature_importance_(self) -> Dict[str, float]:
        """اهمیت فیچر تجمیعی (میانگین وزنی روی همه‌ی مدل‌های عضو)."""
        agg: Dict[str, float] = {c: 0.0 for c in self.feature_columns}
        total_w = sum(m.weight for m in self.members) or 1.0
        for m in self.members:
            for k, v in m.feature_importance.items():
                agg[k] += v * (m.weight / total_w)
        return dict(sorted(agg.items(), key=lambda kv: kv[1], reverse=True))

    # ------------------------------------------------------------------ #
    @classmethod
    def create(cls, backends: Optional[List[str]] = None, **model_kwargs) -> "EnsembleSignalScorer":
        names = backends or DEFAULT_BACKENDS
        members = []
        for name in names:
            try:
                model = _make_member(name, **model_kwargs)
                members.append(_Member(name=name, model=model))
            except ImportError:
                continue  # کتابخانه نصب نیست؛ این عضو ساکت رد می‌شود، بقیه کار می‌کنند
        if not members:
            raise RuntimeError("هیچ مدل عضوی در دسترس نیست (حتی scikit-learn هم نصب نیست).")
        return cls(members=members)

    def fit(self, X: pd.DataFrame, y: pd.Series, val_fraction: float = 0.2) -> "EnsembleSignalScorer":
        """آموزش همه‌ی مدل‌های عضو + محاسبه‌ی وزن هر کدام روی یک برش زمانی نگه‌داشته‌شده.

        X, y باید از قبل به ترتیب زمانی مرتب باشند (خروجی build_training_dataset این‌طور است).
        """
        X = X[self.feature_columns].reset_index(drop=True)
        y = y.reset_index(drop=True)
        self.n_train_samples = len(X)

        self.feature_means_ = {c: float(X[c].mean()) for c in self.feature_columns}
        self.feature_stds_ = {c: float(X[c].std() or 1.0) for c in self.feature_columns}

        n = len(X)
        n_val = max(int(n * val_fraction), 5) if n >= 25 else 0
        n_train = n - n_val

        from sklearn.metrics import roc_auc_score

        for m in self.members:
            # ۱) روی کل داده fit نهایی (برای استفاده در inference)
            m.model.fit(X, y)
            m.feature_importance = _model_feature_importance(m.model, self.feature_columns) or {}

            # ۲) روی برش زمانی نگه‌داشته‌شده AUC را برای وزن‌دهی تخمین می‌زند
            if n_val > 0 and y.iloc[n_train:].nunique() > 1:
                probe_model = _make_member(m.name)
                try:
                    probe_model.fit(X.iloc[:n_train], y.iloc[:n_train])
                    val_proba = probe_model.predict_proba(X.iloc[n_train:])[:, 1]
                    m.val_auc = float(roc_auc_score(y.iloc[n_train:], val_proba))
                except Exception:
                    m.val_auc = 0.5
            else:
                m.val_auc = 0.5

        # وزن‌دهی: softmax روی (AUC - 0.5) که مدل‌های بدون قدرت پیش‌بینی (AUC~0.5) وزن ~صفر بگیرند
        strengths = np.array([max(m.val_auc - 0.5, 0.0) for m in self.members])
        if strengths.sum() <= 1e-9:
            weights = np.ones(len(self.members)) / len(self.members)
        else:
            exp_s = np.exp(strengths * 6.0)  # ضریب تیزکردن تمایز مدل‌های قوی‌تر
            weights = exp_s / exp_s.sum()
        for m, w in zip(self.members, weights):
            m.weight = float(w)

        # معیارهای کلی روی همان برش نگه‌داشته‌شده (برای گزارش، نه انتخاب مدل)
        self.trained_at = _dt.datetime.utcnow().isoformat()
        if n_val > 0 and y.iloc[n_train:].nunique() > 1:
            ensemble_val_proba = self._weighted_proba(X.iloc[n_train:])
            try:
                self.train_metrics = {
                    "ensemble_val_auc": float(roc_auc_score(y.iloc[n_train:], ensemble_val_proba)),
                    "n_train": int(n_train),
                    "n_val": int(n_val),
                    "per_model_val_auc": {m.name: round(m.val_auc, 4) for m in self.members},
                    "per_model_weight": {m.name: round(m.weight, 4) for m in self.members},
                }
            except Exception:
                self.train_metrics = {"n_train": int(n_train), "n_val": int(n_val)}
        else:
            self.train_metrics = {"n_train": int(n_train), "n_val": int(n_val), "note": "داده ناکافی برای ارزیابی هولداوت"}
        return self

    # ------------------------------------------------------------------ #
    def _weighted_proba(self, X: pd.DataFrame) -> np.ndarray:
        total = np.zeros(len(X))
        for m in self.members:
            total += m.weight * m.model.predict_proba(X)[:, 1]
        return total

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X = X[self.feature_columns]
        return self._weighted_proba(X)

    def predict_proba_one(self, feature_row: Dict[str, float]) -> float:
        row = feature_dict_to_row(feature_row)
        X = pd.DataFrame([row])[self.feature_columns]
        return float(self._weighted_proba(X)[0])

    def decide(self, feature_row: Dict[str, float]) -> "Decision":
        """خروجی کامل موتور تصمیم‌گیری: احتمال، Confidence Score، توضیح، و شکست هر مدل."""
        row = feature_dict_to_row(feature_row)
        X = pd.DataFrame([row])[self.feature_columns]

        per_model: Dict[str, float] = {}
        for m in self.members:
            per_model[m.name] = float(m.model.predict_proba(X)[:, 1][0])

        weights = np.array([m.weight for m in self.members])
        probs = np.array([per_model[m.name] for m in self.members])
        probability = float(np.dot(weights, probs))

        # توافق مدل‌ها: انحراف‌معیار وزنی احتمالات (کم = توافق بالا)
        weighted_mean = probability
        agreement_std = float(np.sqrt(np.dot(weights, (probs - weighted_mean) ** 2)))
        agreement_score = max(0.0, 1.0 - agreement_std / 0.25)  # ۰..۱ (۰.۲۵ انحراف ~ عدم توافق کامل)

        certainty_score = min(abs(probability - 0.5) * 2.0, 1.0)  # ۰..۱
        confidence = 0.65 * certainty_score + 0.35 * agreement_score
        confidence = float(max(0.0, min(1.0, confidence)))

        reasons = self._explain(row)

        return Decision(
            probability=probability,
            confidence=confidence,
            agreement_score=agreement_score,
            per_model_probability=per_model,
            per_model_weight={m.name: m.weight for m in self.members},
            top_reasons=reasons,
        )

    def _explain(self, row: Dict[str, float], top_k: int = 5) -> List[Tuple[str, float, str]]:
        """سهم تخمینی هر فیچر در تصمیم را برمی‌گرداند: (نام فیچر، سهم امضادار، متن فارسی).

        سهم = اهمیت‌تجمیعی فیچر × انحراف نرمال‌شده‌ی مقدار آن از میانگین داده‌ی آموزش.
        این یک تقریب سریع است (نه SHAP دقیق) اما جهت و بزرگی اثر را به‌درستی نشان می‌دهد.
        """
        importances = self.feature_importance_
        contributions = []
        for col in self.feature_columns:
            imp = importances.get(col, 0.0)
            mean = self.feature_means_.get(col, 0.0)
            std = self.feature_stds_.get(col, 1.0) or 1.0
            z = (row.get(col, 0.0) - mean) / std
            contribution = imp * z
            contributions.append((col, contribution))

        contributions.sort(key=lambda kv: abs(kv[1]), reverse=True)
        out = []
        for col, contribution in contributions[:top_k]:
            label = FEATURE_LABELS_FA.get(col, col)
            direction = "مثبت (تقویت‌کننده سیگنال)" if contribution > 0 else "منفی (تضعیف‌کننده سیگنال)"
            text = f"{label}: تاثیر {direction}"
            out.append((col, float(contribution), text))
        return out

    # ------------------------------------------------------------------ #
    def save(self, path: str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str) -> "EnsembleSignalScorer":
        obj = joblib.load(Path(path))
        if not isinstance(obj, cls):
            raise TypeError(f"فایل {path} یک EnsembleSignalScorer معتبر نیست.")
        return obj

    def summary(self) -> str:
        lines = [
            f"موتور Ensemble — {len(self.members)} مدل عضو",
            f"تاریخ آموزش (UTC): {self.trained_at}",
            f"تعداد نمونه‌های آموزش: {self.n_train_samples}",
            "وزن و AUC هر مدل:",
        ]
        for m in sorted(self.members, key=lambda x: x.weight, reverse=True):
            lines.append(f"  - {m.name}: وزن={m.weight:.3f}  AUC هولداوت={m.val_auc:.3f}")
        lines.append(f"معیارهای کلی: {self.train_metrics}")
        lines.append("اهمیت فیچرهای تجمیعی (نزولی):")
        for k, v in list(self.feature_importance_.items())[:10]:
            lines.append(f"  - {FEATURE_LABELS_FA.get(k, k)}: {v:.4f}")
        return "\n".join(lines)


@dataclass
class Decision:
    """خروجی کامل Decision Engine برای یک سیگنال منفرد."""

    probability: float                          # احتمال ترکیبی موفقیت (۰..۱)
    confidence: float                            # امتیاز اطمینان نهایی (۰..۱)
    agreement_score: float                       # میزان توافق بین مدل‌های عضو (۰..۱)
    per_model_probability: Dict[str, float]
    per_model_weight: Dict[str, float]
    top_reasons: List[Tuple[str, float, str]]

    def confidence_pct(self) -> float:
        return round(self.confidence * 100, 1)

    def probability_pct(self) -> float:
        return round(self.probability * 100, 1)
