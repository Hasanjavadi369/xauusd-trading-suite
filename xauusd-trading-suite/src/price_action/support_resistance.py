"""
تشخیص سطوح حمایت/مقاومت با خوشه‌بندی نقاط Swing High/Low که چند بار لمس شده‌اند.
"""
from typing import List
import pandas as pd
from ..core.data_models import MarketStructurePoint, Zone


def detect_support_resistance(swing_points: List[MarketStructurePoint],
                               tolerance_pct: float = 0.15,
                               min_touches: int = 2) -> List[Zone]:
    """
    نقاط سوینگ (high و low با هم) را بر اساس نزدیکی قیمتی خوشه‌بندی می‌کند.
    هر خوشه با حداقل `min_touches` لمس، یک سطح حمایت/مقاومت معتبر است.
    """
    zones: List[Zone] = []
    all_points = sorted(swing_points, key=lambda p: p.price)
    used = set()

    for i in range(len(all_points)):
        if i in used:
            continue
        cluster = [all_points[i]]
        for j in range(i + 1, len(all_points)):
            if j in used:
                continue
            diff_pct = abs(all_points[j].price - cluster[0].price) / cluster[0].price * 100
            if diff_pct <= tolerance_pct:
                cluster.append(all_points[j])
                used.add(j)

        if len(cluster) >= min_touches:
            prices = [p.price for p in cluster]
            times = sorted(cluster, key=lambda p: p.timestamp)
            kind = "resistance" if sum(1 for p in cluster if p.kind == "swing_high") >= len(cluster) / 2 else "support"
            zones.append(Zone(
                kind=kind,
                start_time=times[0].timestamp,
                end_time=times[-1].timestamp,
                top=max(prices),
                bottom=min(prices),
                strength=len(cluster),
                metadata={"touches": len(cluster)},
            ))

    return zones
