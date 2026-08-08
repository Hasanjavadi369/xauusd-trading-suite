"""
تشخیص نواحی نقدینگی (Liquidity Pools):
- Equal Highs (EQH): چند سقف تقریباً هم‌سطح -> نقدینگی خرید بالای آن‌ها
- Equal Lows (EQL): چند کف تقریباً هم‌سطح -> نقدینگی فروش زیر آن‌ها
- Liquidity Sweep: قیمت به‌طور آنی نقدینگی را می‌زند و برمی‌گردد (شکار نقدینگی)
"""
from typing import List
import pandas as pd
from ..core.data_models import MarketStructurePoint, Zone


def detect_equal_levels(swing_points: List[MarketStructurePoint], tolerance_pct: float = 0.03) -> List[Zone]:
    zones: List[Zone] = []
    highs = [p for p in swing_points if p.kind == "swing_high"]
    lows = [p for p in swing_points if p.kind == "swing_low"]

    for group, kind in [(highs, "liquidity_eqh"), (lows, "liquidity_eql")]:
        used = set()
        for i in range(len(group)):
            if i in used:
                continue
            cluster = [group[i]]
            for j in range(i + 1, len(group)):
                if j in used:
                    continue
                diff_pct = abs(group[j].price - group[i].price) / group[i].price * 100
                if diff_pct <= tolerance_pct:
                    cluster.append(group[j])
                    used.add(j)
            if len(cluster) >= 2:
                prices = [p.price for p in cluster]
                zones.append(Zone(
                    kind=kind,
                    start_time=cluster[0].timestamp,
                    end_time=cluster[-1].timestamp,
                    top=max(prices),
                    bottom=min(prices),
                    strength=len(cluster),
                    metadata={"points": len(cluster)},
                ))
    return zones


def detect_liquidity_sweep(df: pd.DataFrame, liquidity_zones: List[Zone]) -> List[dict]:
    """
    شکار نقدینگی: قیمت (wick) از سطح liquidity عبور می‌کند اما کندل با close برمی‌گردد
    داخل محدوده (نشانه‌ی برداشت نقدینگی توسط اسمارت‌مانی قبل از حرکت اصلی).
    """
    sweeps = []
    for zone in liquidity_zones:
        end_idx = df[df["time"] == zone.end_time].index
        if len(end_idx) == 0:
            continue
        start_search = end_idx[0] + 1
        level = zone.top if zone.kind == "liquidity_eqh" else zone.bottom

        for i in range(start_search, min(start_search + 50, len(df))):
            if zone.kind == "liquidity_eqh":
                if df["high"].iloc[i] > level and df["close"].iloc[i] < level:
                    sweeps.append({
                        "time": df["time"].iloc[i], "level": level,
                        "type": "sweep_high", "zone": zone,
                    })
                    break
            else:
                if df["low"].iloc[i] < level and df["close"].iloc[i] > level:
                    sweeps.append({
                        "time": df["time"].iloc[i], "level": level,
                        "type": "sweep_low", "zone": zone,
                    })
                    break
    return sweeps
