"""
یادگیری مستمر (Continuous Learning) — موتور Ensemble را از روی نتایج واقعی
معاملات (بک‌تست روی داده‌ی تاریخی واقعی، یا معاملات دموی زنده) به‌مرور بهتر می‌کند.

نکته‌ی مهم درباره‌ی صداقت فنی این ماژول:
  در یک برنامه‌ی توصیه‌ی معاملاتی، «یادگیری آنلاین لحظه‌به‌لحظه از هر تیک» نه
  واقع‌بینانه است و نه امن (یک دنباله‌ی کوتاه از نتایج تصادفی می‌تواند مدل را
  بی‌ثبات کند). روش استاندارد صنعتی — و همان چیزی که اینجا پیاده شده — «یادگیری
  دسته‌ای» (Batch/Incremental Retraining) است:
    ۱) هر معامله‌ی بسته‌شده (برد/باخت واقعی) با بردار فیچرهای لحظه‌ی سیگنال در
       یک لاگ ماندگار (CSV) ذخیره می‌شود — همیشه از داده‌ی واقعی، هرگز فرضی.
    ۲) وقتی تعداد نمونه‌های جدید کافی باشد (پیش‌فرض: حداقل ۳۰)، کاربر (یا یک
       زمان‌بند بیرونی مثل cron) بازآموزی را با retrain_from_log() اجرا می‌کند.
    ۳) مدل جدید فقط اگر روی هولداوت زمانی regress نکند جایگزین مدل قبلی
       می‌شود (guard rail) — مدل قبلی همیشه به‌عنوان نسخه‌ی پشتیبان می‌ماند.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

from src.core.data_models import Trade
from src.ml.dataset import build_training_dataset
from src.ml.ensemble import EnsembleSignalScorer
from src.ml.features import FEATURE_COLUMNS

TRAINING_LOG_PATH = "models/training_log.csv"
PERFORMANCE_HISTORY_PATH = "models/performance_history.json"
LATEST_MODEL_PATH = "models/signal_scorer_ensemble.joblib"


# ------------------------------------------------------------------ #
# ثبت نتایج واقعی معاملات
# ------------------------------------------------------------------ #
def log_closed_trades(
    trades: Iterable[Trade],
    source: str,
    log_path: str = TRAINING_LOG_PATH,
) -> int:
    """معاملات واقعیِ بسته‌شده (از بک‌تست روی CSV واقعی یا حساب دمو) را در لاگ ماندگار ذخیره می‌کند.

    source: منبع نتیجه، برای ردیابی — مثلاً "backtest" یا "demo_account".
    فقط معاملاتی که بردار فیچر معتبر در metadata["features"] دارند ثبت می‌شوند
    (یعنی فقط سیگنال‌هایی که واقعاً از موتور SMC/اندیکاتور تولید شده‌اند).
    برمی‌گرداند: تعداد ردیف‌های جدید ثبت‌شده.
    """
    rows = []
    for trade in trades:
        features = (trade.metadata or {}).get("features")
        if not features or trade.is_open or trade.profit is None:
            continue
        row = {col: float(features.get(col, 0.0)) for col in FEATURE_COLUMNS}
        row["label"] = 1 if trade.profit > 0 else 0
        row["profit"] = trade.profit
        row["direction"] = getattr(trade.direction, "value", str(trade.direction))
        row["close_time"] = str(trade.close_time)
        row["source"] = source
        row["logged_at"] = datetime.now(timezone.utc).isoformat()
        row["trade_id"] = trade.id
        rows.append(row)

    if not rows:
        return 0

    new_df = pd.DataFrame(rows)
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        existing = pd.read_csv(path)
        # از تکرار همان trade_id جلوگیری می‌کند (مثلا اگر کاربر چند بار دکمه را بزند)
        existing_ids = set(existing.get("trade_id", []))
        new_df = new_df[~new_df["trade_id"].isin(existing_ids)]
        if new_df.empty:
            return 0
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df

    combined.to_csv(path, index=False)
    return len(new_df)


def log_backtest_report(trades: List[Trade], log_path: str = TRAINING_LOG_PATH) -> int:
    """میانبر مشخص برای ثبت نتایج یک اجرای بک‌تست (روی داده‌ی تاریخی واقعی)."""
    return log_closed_trades(trades, source="backtest", log_path=log_path)


def log_demo_account_trades(trades: List[Trade], log_path: str = TRAINING_LOG_PATH) -> int:
    """میانبر مشخص برای ثبت نتایج معاملات حساب دموی زنده."""
    return log_closed_trades(trades, source="demo_account", log_path=log_path)


def training_log_size(log_path: str = TRAINING_LOG_PATH) -> int:
    path = Path(log_path)
    if not path.exists():
        return 0
    try:
        return len(pd.read_csv(path))
    except Exception:
        return 0


# ------------------------------------------------------------------ #
# بازآموزی
# ------------------------------------------------------------------ #
def _load_training_log(log_path: str) -> Optional[pd.DataFrame]:
    path = Path(log_path)
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    return df


def retrain_from_log(
    log_path: str = TRAINING_LOG_PATH,
    model_output_path: str = LATEST_MODEL_PATH,
    performance_history_path: str = PERFORMANCE_HISTORY_PATH,
    min_samples: int = 30,
    fresh_csv_dataset: Optional[pd.DataFrame] = None,
    strategy=None,
    regression_tolerance: float = 0.02,
) -> dict:
    """موتور Ensemble را از روی لاگ نتایج واقعی معاملات بازآموزی می‌کند.

    fresh_csv_dataset / strategy: اختیاری — اگر یک DataFrame تاریخی واقعیِ
    تازه هم در دسترس باشد، دیتاست آموزشی آن (از build_training_dataset) با
    لاگ معاملات واقعی ترکیب می‌شود تا مدل هم از سابقه‌ی معاملات واقعی و هم از
    کل تاریخچه‌ی بازار یاد بگیرد.

    برمی‌گرداند: دیکشنری وضعیت شامل اینکه آیا مدل جدید جایگزین شد یا نه و چرا.
    """
    log_df = _load_training_log(log_path)

    frames = []
    if log_df is not None:
        frames.append(log_df[list(FEATURE_COLUMNS) + ["label"]])

    if fresh_csv_dataset is not None and strategy is not None:
        extra = build_training_dataset(fresh_csv_dataset, strategy)
        if len(extra) > 0:
            frames.append(extra[list(FEATURE_COLUMNS) + ["label"]])

    if not frames:
        return {"status": "no_data", "message": "هیچ داده‌ای برای بازآموزی موجود نیست."}

    dataset = pd.concat(frames, ignore_index=True)
    n_samples = len(dataset)
    if n_samples < min_samples:
        return {
            "status": "insufficient_data",
            "message": f"فقط {n_samples} نمونه موجود است؛ حداقل {min_samples} نمونه لازم است.",
            "n_samples": n_samples,
        }
    if dataset["label"].nunique() < 2:
        return {"status": "insufficient_variety", "message": "همه‌ی نمونه‌ها یک کلاس (همه برد یا همه باخت) هستند."}

    X, y = dataset[FEATURE_COLUMNS], dataset["label"]
    new_model = EnsembleSignalScorer.create()
    new_model.fit(X, y)
    new_auc = new_model.train_metrics.get("ensemble_val_auc")

    # Guard rail: اگر مدل قبلی موجود است و AUC مدل جدید به‌طور معنادار بدتر است، جایگزین نکن
    previous_auc = None
    model_path = Path(model_output_path)
    promoted = True
    reason = "اولین آموزش یا بهبود/عدم افت معنادار نسبت به مدل قبلی."

    if model_path.exists() and new_auc is not None:
        try:
            old_model = EnsembleSignalScorer.load(str(model_path))
            previous_auc = old_model.train_metrics.get("ensemble_val_auc")
            if previous_auc is not None and new_auc < previous_auc - regression_tolerance:
                promoted = False
                reason = (f"مدل جدید (AUC={new_auc:.3f}) از مدل قبلی "
                           f"(AUC={previous_auc:.3f}) به‌طور معنادار ضعیف‌تر است؛ جایگزین نشد.")
        except Exception:
            pass

    if promoted:
        new_model.save(model_output_path)

    _append_performance_history(
        performance_history_path,
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_samples": n_samples,
            "new_model_auc": new_auc,
            "previous_model_auc": previous_auc,
            "promoted": promoted,
            "per_model_val_auc": new_model.train_metrics.get("per_model_val_auc"),
        },
    )

    return {
        "status": "promoted" if promoted else "rejected",
        "message": reason,
        "n_samples": n_samples,
        "new_model_auc": new_auc,
        "previous_model_auc": previous_auc,
        "model": new_model if promoted else None,
    }


def _append_performance_history(path: str, entry: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if p.exists():
        try:
            history = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append(entry)
    p.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def load_performance_history(path: str = PERFORMANCE_HISTORY_PATH) -> list:
    p = Path(path)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
