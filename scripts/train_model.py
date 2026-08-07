"""
آموزش مدل یادگیری ماشین روی داده‌ی تاریخی و ذخیره‌ی آرتیفکت مدل.

مثال اجرا:
    python scripts/train_model.py --csv data/sample_xauusd_h1.csv \
        --out models/xauusd_model.joblib
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from src.core.utils import load_config, get_logger
from src.indicators.calculator import compute_all_indicators
from src.price_action.candlestick_patterns import detect_all_patterns
from src.ml.feature_engineering import build_features, clean_features_labels
from src.ml.labeling import triple_barrier_labels, label_distribution
from src.ml.model import MLSignalModel

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="آموزش مدل یادگیری ماشین XAUUSD Trading Suite")
    parser.add_argument("--csv", required=True, help="مسیر فایل CSV داده تاریخی")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--out", default="models/xauusd_model.joblib")
    parser.add_argument("--report-out", default="models/train_report.json")
    args = parser.parse_args()

    config = load_config(args.config)
    ai_cfg = config.get("ai", {})

    df = pd.read_csv(args.csv)
    time_col = "datetime" if "datetime" in df.columns else "time"
    df = df.rename(columns={time_col: "time"})
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    logger.info(f"{len(df)} کندل بارگذاری شد؛ در حال محاسبه اندیکاتورها...")
    df = compute_all_indicators(df, config)
    df = detect_all_patterns(df)

    logger.info("در حال برچسب‌گذاری Triple-Barrier بر اساس رفتار آینده قیمت...")
    labels = triple_barrier_labels(
        df, df["atr"],
        tp_atr_mult=ai_cfg.get("tp_atr_mult", 2.0),
        sl_atr_mult=ai_cfg.get("sl_atr_mult", 1.0),
        max_horizon_bars=ai_cfg.get("max_horizon_bars", 20),
    )
    dist = label_distribution(labels)
    logger.info(f"توزیع برچسب‌ها: {dist}")

    features = build_features(df)
    X, y = clean_features_labels(features, labels)
    logger.info(f"{len(X)} نمونه‌ی معتبر برای آموزش/تست آماده شد.")

    model = MLSignalModel(model_type=ai_cfg.get("model_type", "gradient_boosting"))
    report = model.train(X, y, test_size=ai_cfg.get("test_size", 0.2))

    logger.info(f"دقت آموزش: {report.train_accuracy} | دقت تست: {report.test_accuracy}")
    logger.info("گزارش کامل طبقه‌بندی روی داده تست:\n" + report.classification_report_text)
    logger.info("۵ ویژگی مهم:")
    for i, (feat, importance) in enumerate(report.feature_importances.items()):
        if i >= 5:
            break
        logger.info(f"  {feat}: {importance}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    model.save(args.out)
    model.save_report(report, args.report_out)
    logger.info(f"مدل ذخیره شد: {args.out}")
    logger.info(f"گزارش آموزش ذخیره شد: {args.report_out}")


if __name__ == "__main__":
    main()
