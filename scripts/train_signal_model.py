"""
آموزش مدل امتیازدهی سیگنال (Signal Scoring Model).

این اسکریپت:
  1) داده‌ی CSV تاریخی را می‌خواند و اندیکاتورها را محاسبه می‌کند.
  2) با اجرای walk-forward استراتژی SMC روی کل تاریخچه (دقیقاً همان‌طور که در
     بک‌تست/زنده مصرف می‌شود)، یک دیتاست برچسب‌خورده از سیگنال‌های گذشته می‌سازد
     (هر سیگنال -> فیچرهای لحظه‌ی صدور + برچسب برد/باخت).
  3) دیتاست را به‌صورت زمانی (نه تصادفی، تا نشتِ اطلاعات از آینده به گذشته رخ
     ندهد) به train/test تقسیم می‌کند.
  4) یک classifier (XGBoost در صورت نصب بودن، وگرنه LightGBM، وگرنه
     HistGradientBoostingClassifier از scikit-learn) را train و ارزیابی می‌کند.
  5) مدل + متادیتای آموزش (معیارها، اهمیت فیچرها) را در models/ ذخیره می‌کند.

مثال اجرا:
    python -m scripts.train_signal_model --csv data/XAUUSD_H1_real.csv
    python -m scripts.train_signal_model --csv data/my_5years_h1.csv \
        --backend ensemble --output models/signal_scorer_ensemble.joblib

نکته: با دیتاست‌های کوچک (مثل داده‌ی نمونه‌ی خود پروژه) تعداد سیگنال‌های
برچسب‌خورده کم است (چند ده‌تا) و مدل صرفاً برای نمایش/تست کار می‌کند نه استفاده‌ی
واقعی. برای یک مدل قابل‌اعتماد به چند سال داده‌ی H1 (یا تایم‌فریم پایین‌تر با
داده‌ی بیشتر) نیاز است تا حداقل چند صد سیگنال برچسب‌خورده جمع شود.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# اجازه می‌دهد این اسکریپت هم به‌صورت مستقیم (python scripts/train_signal_model.py)
# و هم به‌صورت ماژول (python -m scripts.train_signal_model) از ریشه‌ی پروژه اجرا شود.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
)

from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.ml.dataset import build_training_dataset
from src.ml.scorer import SignalScorer
from src.ml.ensemble import EnsembleSignalScorer
from src.ml.features import FEATURE_COLUMNS


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["datetime"])
    df = df.rename(columns={"datetime": "time"})
    return df.sort_values("time").reset_index(drop=True)


def chronological_split(dataset: pd.DataFrame, test_size: float):
    dataset = dataset.sort_values("timestamp").reset_index(drop=True)
    split_at = int(len(dataset) * (1 - test_size))
    return dataset.iloc[:split_at], dataset.iloc[split_at:]


def evaluate(scorer: SignalScorer, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    proba = scorer.predict_proba(X_test)
    pred = (proba >= 0.5).astype(int)

    metrics = {
        "n_test": int(len(y_test)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
    }
    # AUC فقط وقتی معنی‌دار است که هر دو کلاس در تست حاضر باشند
    if y_test.nunique() > 1:
        metrics["roc_auc"] = round(float(roc_auc_score(y_test, proba)), 4)
    else:
        metrics["roc_auc"] = None

    cm = confusion_matrix(y_test, pred, labels=[0, 1])
    metrics["confusion_matrix"] = {"tn": int(cm[0, 0]), "fp": int(cm[0, 1]),
                                    "fn": int(cm[1, 0]), "tp": int(cm[1, 1])}

    # baseline مقایسه‌ای: خطای اطمینان قانون‌محور خام (rule_confidence) بدون مدل،
    # فقط برای اینکه معلوم شود مدل چقدر نسبت به heuristic اولیه بهتر شده
    baseline_pred = (X_test["rule_confidence"] >= 0.5).astype(int)
    metrics["baseline_rule_confidence_accuracy"] = round(
        float(accuracy_score(y_test, baseline_pred)), 4
    )
    return metrics


def main():
    parser = argparse.ArgumentParser(description="آموزش مدل امتیازدهی سیگنال SMC")
    parser.add_argument("--csv", required=True, help="مسیر CSV تاریخی (ستون‌ها: datetime, open, high, low, close, volume)")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--backend", default="ensemble",
                         choices=["ensemble", "auto", "xgboost", "lightgbm", "sklearn"],
                         help="ensemble (پیش‌فرض) = موتور Decision Engine با چند مدل ترکیبی؛ "
                              "بقیه = مدل تک‌بک‌اند قدیمی (src/ml/scorer.py)")
    parser.add_argument("--output", default="models/signal_scorer_ensemble.joblib")
    parser.add_argument("--test-size", type=float, default=0.25, help="سهم داده‌ی تست (تقسیم زمانی، نه تصادفی)")
    parser.add_argument("--analysis-window-bars", type=int, default=None,
                         help="پیش‌فرض: config.smc.analysis_window_bars یا ۲۰۰")
    parser.add_argument("--check-interval", type=int, default=None,
                         help="پیش‌فرض: config.backtest.signal_check_interval یا ۳")
    parser.add_argument("--warmup-bars", type=int, default=100)
    parser.add_argument("--max-horizon-bars", type=int, default=200,
                         help="حداکثر تعداد کندل برای منتظر ماندن رسیدن به TP/SL؛ سیگنال‌های ناتمام دور ریخته می‌شوند")
    parser.add_argument("--n-estimators", type=int, default=300)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    args = parser.parse_args()

    config = load_config(args.config)
    analysis_window_bars = args.analysis_window_bars or config.get("smc", {}).get("analysis_window_bars", 200)
    check_interval = args.check_interval or config.get("backtest", {}).get("signal_check_interval", 3)

    print(f"[۱/۵] در حال خواندن {args.csv} و محاسبه‌ی اندیکاتورها ...")
    df = load_csv(args.csv)
    df = compute_all_indicators(df, config)
    strategy = SMCConfluenceStrategy(config)  # بدون scorer — فقط برای تولید سیگنال قانون‌محور
    df = strategy.prepare(df)

    print(f"[۲/۵] در حال ساخت دیتاست برچسب‌خورده (walk-forward روی {len(df)} کندل) ...")
    dataset = build_training_dataset(
        df, strategy,
        analysis_window_bars=analysis_window_bars,
        check_interval=check_interval,
        warmup_bars=args.warmup_bars,
        max_horizon_bars=args.max_horizon_bars,
    )
    print(f"      {len(dataset)} سیگنال برچسب‌خورده پیدا شد "
          f"(برد={int((dataset['label']==1).sum()) if len(dataset) else 0}, "
          f"باخت={int((dataset['label']==0).sum()) if len(dataset) else 0})")

    if len(dataset) < 30:
        print("      هشدار: تعداد سیگنال‌ها برای آموزش قابل‌اعتماد کم است. "
              "پیشنهاد می‌شود از یک بازه‌ی تاریخی طولانی‌تر (چند سال) استفاده کنید.")
    if len(dataset) < 5:
        raise SystemExit("داده‌ی کافی برای آموزش وجود ندارد.")

    print("[۳/۵] در حال تقسیم زمانی train/test ...")
    train_df, test_df = chronological_split(dataset, args.test_size)
    X_train, y_train = train_df[FEATURE_COLUMNS], train_df["label"]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df["label"]
    print(f"      train={len(train_df)} | test={len(test_df)}")

    print(f"[۴/۵] در حال آموزش مدل (backend={args.backend}) ...")
    if args.backend == "ensemble":
        scorer = EnsembleSignalScorer.create(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
        )
        scorer.fit(X_train, y_train)
    else:
        scorer = SignalScorer.create(
            backend=args.backend,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
        )
        scorer.fit(X_train, y_train)
    print(f"      بک‌اند نهایی استفاده‌شده: {scorer.backend_name}")

    metrics = {}
    if len(test_df) > 0:
        metrics = evaluate(scorer, X_test, y_test)
        print("      معیارهای ارزیابی روی داده‌ی تست (هولداوت خارجی):")
        for k, v in metrics.items():
            print(f"        {k}: {v}")
    else:
        print("      داده‌ی تست خالی است (دیتاست خیلی کوچک)؛ ارزیابی رد شد.")

    if args.backend == "ensemble":
        # train_metrics داخلی Ensemble (وزن/AUC هر مدل عضو) را نگه می‌داریم و معیار
        # تست خارجی نهایی را هم به‌عنوان کلید جدا اضافه می‌کنیم (چیزی حذف نمی‌شود).
        scorer.train_metrics = {**scorer.train_metrics, "external_test_metrics": metrics}
        print("\n" + scorer.summary())
    else:
        scorer.train_metrics = metrics

    print(f"[۵/۵] در حال ذخیره‌ی مدل در {args.output} ...")
    scorer.save(args.output)

    meta_path = Path(args.output).with_suffix(".meta.json")
    meta = {
        "backend": scorer.backend_name,
        "trained_at": scorer.trained_at,
        "feature_columns": FEATURE_COLUMNS,
        "dataset_size": len(dataset),
        "train_size": len(train_df),
        "test_size": len(test_df),
        "metrics": metrics,
        "feature_importance": scorer.feature_importance_,
        "source_csv": args.csv,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      متادیتا ذخیره شد در {meta_path}")
    print("\nتمام. برای استفاده در بک‌تست/زنده، مسیر مدل را در config.yaml بخش ml.model_path تنظیم کنید.")


if __name__ == "__main__":
    main()
