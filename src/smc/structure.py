"""
تحلیل ساختار بازار (Market Structure) بر اساس مفاهیم ICT/SMC:
- تشخیص Swing High / Swing Low
- تشخیص BOS (Break of Structure)
- تشخیص CHOCH (Change of Character)
"""
from typing import List
import pandas as pd
from ..core.data_models import MarketStructurePoint


def find_swing_points(df: pd.DataFrame, lookback: int = 5) -> List[MarketStructurePoint]:
    """
    یک کندل، Swing High است اگر high آن از `lookback` کندل چپ و راست بیشتر باشد
    (و مشابه برای Swing Low). این روش استاندارد fractal-based است.
    """
    points: List[MarketStructurePoint] = []
    highs = df["high"].values
    lows = df["low"].values
    n = len(df)

    for i in range(lookback, n - lookback):
        window_high = highs[i - lookback:i + lookback + 1]
        window_low = lows[i - lookback:i + lookback + 1]

        if highs[i] == window_high.max() and (window_high == window_high.max()).sum() == 1:
            points.append(MarketStructurePoint(
                timestamp=df["time"].iloc[i], price=highs[i], kind="swing_high", index=i
            ))
        if lows[i] == window_low.min() and (window_low == window_low.min()).sum() == 1:
            points.append(MarketStructurePoint(
                timestamp=df["time"].iloc[i], price=lows[i], kind="swing_low", index=i
            ))

    points.sort(key=lambda p: p.index)
    return points


def detect_bos_choch(df: pd.DataFrame, swing_points: List[MarketStructurePoint]) -> List[MarketStructurePoint]:
    """
    منطق ساده‌شده و قابل‌فهم BOS/CHOCH:
    - روند صعودی یعنی توالی Higher-High/Higher-Low. اگر قیمت زیر آخرین Swing Low
      معتبرِ روند صعودی بسته شود => CHOCH (تغییر ساختار به نزولی).
    - وقتی در همان جهت روند فعلی، سقف/کف قبلی شکسته شود => BOS (ادامه روند).
    """
    events: List[MarketStructurePoint] = []
    if len(swing_points) < 2:
        return events

    trend = None  # "up" یا "down"
    last_high = None
    last_low = None

    for point in swing_points:
        if point.kind == "swing_high":
            if last_high is not None:
                if point.price > last_high.price:
                    if trend == "down":
                        events.append(MarketStructurePoint(
                            point.timestamp, point.price, "CHOCH_bullish", point.index))
                        trend = "up"
                    elif trend == "up":
                        events.append(MarketStructurePoint(
                            point.timestamp, point.price, "BOS_bullish", point.index))
            last_high = point
        else:  # swing_low
            if last_low is not None:
                if point.price < last_low.price:
                    if trend == "up":
                        events.append(MarketStructurePoint(
                            point.timestamp, point.price, "CHOCH_bearish", point.index))
                        trend = "down"
                    elif trend == "down":
                        events.append(MarketStructurePoint(
                            point.timestamp, point.price, "BOS_bearish", point.index))
            last_low = point

        if trend is None and last_high is not None and last_low is not None:
            trend = "up" if last_high.index < last_low.index else "down"

    return events


def current_trend(swing_points: List[MarketStructurePoint], events: List[MarketStructurePoint]) -> str:
    """آخرین جهت ساختار بازار را برمی‌گرداند: 'up', 'down' یا 'unknown'."""
    if not events:
        return "unknown"
    last_event = events[-1]
    if "bullish" in last_event.kind:
        return "up"
    if "bearish" in last_event.kind:
        return "down"
    return "unknown"
