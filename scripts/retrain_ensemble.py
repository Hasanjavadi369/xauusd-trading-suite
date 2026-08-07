"""
بازآموزی (Continuous Learning) موتور Ensemble از روی نتایج واقعی معاملات.

این اسکریپت لاگ ماندگار نتایج معاملات واقعی (``models/training_log.csv`` —
ثبت‌شده توسط بک‌تست روی داده‌ی تاریخی واقعی یا حساب دموی داشبورد) را می‌خواند
و در صورت کافی بودن تعداد نمونه‌ها، مدل Ensemble را بازآموزی می‌کند. اگر یک
CSV تاریخی تازه هم بدهید، دیتاست آموزشی آن هم به لاگ اضافه می‌شود.

مثال اجرا:
    python -m scripts.retrain_ensemble
    python -m scripts.retrain_ensemble --fresh-csv data/XAUUSD_H1_real_latest.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd
import yaml

from src.indicators.calculator import compute_all_indicators
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.ml.continuous_learning import (
    retrain_from_log, TRAINING_LOG_PATH, LATEST_MODEL_PATH, PERFORMANCE_HISTORY_PATH,
    training_log_size,
)


def main():
    parser = argparse.ArgumentParser(description="بازآموزی موتور Ensemble از روی نتایج واقعی معاملات")
    parser.add_argument("--log", default=TRAINING_LOG_PATH)
    parser.add_argument("--output", default=LATEST_MODEL_PATH)
    parser.add_argument("--performance-history", default=PERFORMANCE_HISTORY_PATH)
    parser.add_argument("--min-samples", type=int, default=30)
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--fresh-csv", default=None,
                         help="اختیاری: مسیر یک CSV تاریخی واقعی تازه برای غنی‌سازی داده‌ی آموزش")
    args = parser.parse_args()

    n_log = training_log_size(args.log)
    print(f"لاگ نتایج معاملات واقعی: {n_log} نمونه در {args.log}")

    fresh_df, strategy = None, None
    if args.fresh_csv:
        with open(args.config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        fresh_df = pd.read_csv(args.fresh_csv, parse_dates=["datetime"])
        fresh_df = fresh_df.rename(columns={"datetime": "time"}).sort_values("time").reset_index(drop=True)
        fresh_df = compute_all_indicators(fresh_df, config)
        strategy = SMCConfluenceStrategy(config)
        fresh_df = strategy.prepare(fresh_df)
        print(f"CSV تازه بارگذاری شد: {len(fresh_df)} کندل از {args.fresh_csv}")

    result = retrain_from_log(
        log_path=args.log,
        model_output_path=args.output,
        performance_history_path=args.performance_history,
        min_samples=args.min_samples,
        fresh_csv_dataset=fresh_df,
        strategy=strategy,
    )

    print(f"\nوضعیت: {result['status']}")
    print(f"پیام: {result['message']}")
    if "n_samples" in result:
        print(f"تعداد کل نمونه‌های آموزش: {result['n_samples']}")
    if result.get("new_model_auc") is not None:
        print(f"AUC مدل جدید (هولداوت داخلی): {result['new_model_auc']:.4f}")
    if result.get("previous_model_auc") is not None:
        print(f"AUC مدل قبلی: {result['previous_model_auc']:.4f}")

    if result["status"] == "promoted":
        print(f"\n✅ مدل جدید ذخیره و جایگزین شد: {args.output}")
    elif result["status"] == "rejected":
        print("\n⚠️ مدل جدید رد شد (افت معنادار عملکرد)؛ مدل قبلی همچنان فعال است.")
    else:
        print(f"\nℹ️ بازآموزی انجام نشد ({result['status']}).")


if __name__ == "__main__":
    main()
