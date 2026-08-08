"""ابزارهای کمکی مشترک: بارگذاری تنظیمات، لاگ، اعتبارسنجی دیتافریم."""
import logging
import os
import yaml
import pandas as pd

REQUIRED_OHLC_COLUMNS = ["time", "open", "high", "low", "close", "volume"]


def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def validate_ohlc_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """اطمینان از وجود ستون‌های لازم و مرتب بودن بر اساس زمان."""
    missing = [c for c in REQUIRED_OHLC_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"ستون‌های ضروری در دیتافریم موجود نیست: {missing}")
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df


def load_ohlc_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"فایل داده یافت نشد: {path}")
    df = pd.read_csv(path)
    return validate_ohlc_dataframe(df)
