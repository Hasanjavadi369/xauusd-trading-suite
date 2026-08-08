"""
Live XAUUSD multi-layer signal engine.

Pipeline:
Live price -> multi-timeframe -> structure -> SMC/ICT/liquidity ->
candles/technical -> volatility/momentum -> optional trained AI ->
weighted signal score -> BUY/SELL/NO TRADE -> Entry/SL/TP.

The engine never fabricates market data. AI is only considered active when a
previously trained, real-data model can be loaded.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import math
import pandas as pd

from src.indicators.calculator import compute_all_indicators
from src.price_action import candlestick_patterns
from src.smc import structure, liquidity, fvg as fvg_mod, order_blocks
from src.strategy.signal_engine import SMCConfluenceStrategy
from src.risk_management.levels import validate_levels
from src.core.data_models import TradeDirection
from src.market.multi_timeframe import analyze_timeframes


@dataclass
class LayerScore:
    name: str
    score: float
    direction: str
    details: Dict[str, Any]


@dataclass
class FinalSignal:
    status: str
    confidence: float
    entry: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    rr: float = 0.0
    live_price: Optional[float] = None
    timestamp: str = ""
    layers: Dict[str, Dict[str, Any]] | None = None
    reasons: list[str] | None = None
    ai_active: bool = False
    ai_probability: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(x)))


def _dir_sign(direction: str) -> int:
    return 1 if direction in ("BUY", "LONG", "up", "bullish") else -1 if direction in ("SELL", "SHORT", "down", "bearish") else 0


def _direction_from_trend(t: str) -> str:
    return "BUY" if t == "up" else "SELL" if t == "down" else "NONE"


def _prepare(df: pd.DataFrame, config: Mapping[str, Any]) -> pd.DataFrame:
    d = df.copy()
    if "timestamp" in d.columns and "time" not in d.columns:
        d = d.rename(columns={"timestamp": "time"})
    required = ["time", "open", "high", "low", "close"]
    if any(c not in d.columns for c in required):
        raise ValueError("OHLC data must contain time/open/high/low/close.")
    if "volume" not in d.columns:
        d["volume"] = 0.0
    d["time"] = pd.to_datetime(d["time"], utc=True, errors="coerce")
    for c in ["open", "high", "low", "close", "volume"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=required).sort_values("time").drop_duplicates("time").reset_index(drop=True)
    if len(d) < 80:
        raise ValueError("At least 80 real candles are required for the live analysis.")
    d = compute_all_indicators(d, dict(config))
    d = candlestick_patterns.detect_all_patterns(d)
    return d


def _structure_layer(df: pd.DataFrame, config: Mapping[str, Any]) -> LayerScore:
    lookback = int(config.get("smc", {}).get("swing_lookback", 5))
    swings = structure.find_swing_points(df, lookback)
    events = structure.detect_bos_choch(df, swings)
    trend = structure.current_trend(swings, events)
    direction = _direction_from_trend(trend)
    score = 50.0 if direction == "NONE" else 70.0
    if events:
        last = events[-1]
        if ("bullish" in last.kind and direction == "BUY") or ("bearish" in last.kind and direction == "SELL"):
            score += 15
    # Recent swing sequence adds a modest confirmation.
    recent = swings[-8:]
    highs = [p.price for p in recent if p.kind == "swing_high"]
    lows = [p.price for p in recent if p.kind == "swing_low"]
    if direction == "BUY" and len(highs) >= 2 and len(lows) >= 2 and highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        score += 15
    if direction == "SELL" and len(highs) >= 2 and len(lows) >= 2 and highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        score += 15
    return LayerScore("structure", _clip(score), direction, {
        "trend": trend, "swing_count": len(swings),
        "last_event": events[-1].kind if events else None,
    })


def _liquidity_layer(df: pd.DataFrame, config: Mapping[str, Any]) -> LayerScore:
    lookback = int(config.get("smc", {}).get("swing_lookback", 5))
    swings = structure.find_swing_points(df, lookback)
    zones = liquidity.detect_equal_levels(
        swings, float(config.get("smc", {}).get("liquidity_equal_tolerance_pct", 0.03))
    )
    sweeps = liquidity.detect_liquidity_sweep(df, zones)
    price = float(df["close"].iloc[-1])
    atr = float(df["atr"].iloc[-1]) if pd.notna(df["atr"].iloc[-1]) else 0.0
    recent = [s for s in sweeps if (df["time"].iloc[-1] - s["time"]).total_seconds() <= 50 * 60 * 60]
    buy = sum(1 for s in recent if s["type"] == "sweep_low")
    sell = sum(1 for s in recent if s["type"] == "sweep_high")
    direction = "BUY" if buy > sell else "SELL" if sell > buy else "NONE"
    score = 50.0
    if direction != "NONE":
        score += 20.0 + min(25.0, 10.0 * abs(buy - sell))
    nearby = 0
    if atr > 0:
        for z in zones[-20:]:
            if z.bottom - 1.5 * atr <= price <= z.top + 1.5 * atr:
                nearby += 1
        score += min(15.0, nearby * 5.0)
    return LayerScore("liquidity", _clip(score), direction, {
        "equal_levels": len(zones), "recent_sweeps": len(recent),
        "sweep_low": buy, "sweep_high": sell, "nearby_liquidity": nearby,
    })


def _technical_layer(df: pd.DataFrame) -> LayerScore:
    r = df.iloc[-1]
    price = float(r["close"])
    bullish = 0
    bearish = 0
    reasons = []
    ema20, ema50 = r.get("ema_20"), r.get("ema_50")
    if pd.notna(ema20) and pd.notna(ema50):
        if ema20 > ema50 and price > ema20:
            bullish += 2; reasons.append("EMA trend bullish")
        elif ema20 < ema50 and price < ema20:
            bearish += 2; reasons.append("EMA trend bearish")
    rsi = float(r["rsi"]) if pd.notna(r.get("rsi")) else 50.0
    if 50 < rsi < 70:
        bullish += 1
    elif 30 < rsi < 50:
        bearish += 1
    macd = float(r.get("macd_hist", 0.0) or 0.0)
    if macd > 0: bullish += 1
    elif macd < 0: bearish += 1
    adx = float(r.get("adx", 0.0) or 0.0)
    if adx >= 20:
        if bullish > bearish: bullish += 1
        elif bearish > bullish: bearish += 1
    direction = "BUY" if bullish > bearish else "SELL" if bearish > bullish else "NONE"
    total = bullish + bearish
    score = 50.0 + (25.0 * abs(bullish - bearish) / max(1, total)) + (10.0 if adx >= 20 else 0)
    return LayerScore("technical", _clip(score), direction, {
        "rsi": round(rsi, 2), "macd_hist": round(macd, 5),
        "adx": round(adx, 2), "bullish_points": bullish, "bearish_points": bearish,
        "reasons": reasons,
    })


def _candle_layer(df: pd.DataFrame) -> LayerScore:
    r = df.iloc[-1]
    bull = bool(r.get("pattern_bullish_pin", False) or r.get("pattern_bullish_engulfing", False))
    bear = bool(r.get("pattern_bearish_pin", False) or r.get("pattern_bearish_engulfing", False))
    direction = "BUY" if bull and not bear else "SELL" if bear and not bull else "NONE"
    return LayerScore("candles", 75.0 if direction != "NONE" else 50.0, direction, {
        "bullish_pattern": bull, "bearish_pattern": bear
    })


def _volatility_layer(df: pd.DataFrame) -> LayerScore:
    r = df.iloc[-1]
    atr = float(r["atr"]) if pd.notna(r.get("atr")) else 0.0
    price = float(r["close"])
    atr_pct = atr / price if price else 0.0
    adx = float(r.get("adx", 0.0) or 0.0)
    # Avoid pretending volatility itself has a directional edge.
    score = 55.0 if atr > 0 and 0.0002 <= atr_pct <= 0.03 else 40.0
    if adx >= 20: score += 15.0
    return LayerScore("volatility_momentum", _clip(score), "NONE", {
        "atr": atr, "atr_pct": atr_pct, "adx": adx
    })


def _mtf_layer(frames: Mapping[str, pd.DataFrame]) -> LayerScore:
    views = analyze_timeframes(dict(frames))
    if not views:
        return LayerScore("multi_timeframe", 0.0, "NONE", {})
    # Use higher TFs as confirmation, lower TFs as timing.
    weights = {"M5": 0.8, "M15": 1.0, "M30": 1.1, "H1": 1.3, "H4": 1.5, "D1": 1.7}
    buy = sell = total = 0.0
    detail = {}
    for v in views:
        w = weights.get(v.timeframe, 1.0)
        total += w
        t = v.trend
        detail[v.timeframe] = {"trend": t, "regime": v.regime, "score": round(float(v.score), 3)}
        if t == "up": buy += w * (0.5 + 0.5 * float(v.score))
        elif t == "down": sell += w * (0.5 + 0.5 * float(v.score))
    if total == 0:
        return LayerScore("multi_timeframe", 0.0, "NONE", detail)
    edge = (buy - sell) / total
    direction = "BUY" if edge > 0.12 else "SELL" if edge < -0.12 else "NONE"
    score = 50.0 + min(45.0, abs(edge) * 100.0)
    return LayerScore("multi_timeframe", _clip(score), direction, detail)


def _load_ai(model_path: str):
    p = Path(model_path)
    if not p.is_absolute():
        p = Path(__file__).resolve().parents[2] / p
    if not p.exists():
        return None
    try:
        from src.ml.ensemble import EnsembleSignalScorer
        return EnsembleSignalScorer.load(str(p))
    except Exception:
        return None


def _ai_layer(features: Dict[str, float], model_path: str, candidate_direction: str) -> LayerScore:
    model = _load_ai(model_path)
    if model is None:
        return LayerScore("ai", 0.0, "NONE", {"active": False, "reason": "trained real-data model not available"})
    try:
        decision = model.decide(features)
        p = float(decision.probability)
        # Probability is probability of TP for the candidate, not BUY/SELL direction.
        direction = candidate_direction if p >= 0.5 else ("SELL" if candidate_direction == "BUY" else "BUY")
        score = float(decision.confidence_pct())
        return LayerScore("ai", _clip(score), direction, {
            "active": True, "probability": p, "confidence": decision.confidence_pct(),
            "agreement": decision.agreement_score, "models": decision.per_model_probability,
            "reasons": [x[2] for x in decision.top_reasons],
        })
    except Exception as exc:
        return LayerScore("ai", 0.0, "NONE", {"active": False, "reason": str(exc)})


def _levels(direction: str, entry: float, atr: float, zone_top: float, zone_bottom: float, rr: float) -> tuple[float,float,float] | None:
    if atr <= 0: return None
    buffer = 0.20 * atr
    min_risk = 0.50 * atr
    if direction == "BUY":
        sl = min(zone_bottom - buffer, entry - min_risk)
        risk = entry - sl
        tp = entry + max(rr * risk, 1.5 * atr)
    else:
        sl = max(zone_top + buffer, entry + min_risk)
        risk = sl - entry
        tp = entry - max(rr * risk, 1.5 * atr)
    if risk <= 0 or not validate_levels(
        TradeDirection.LONG if direction == "BUY" else TradeDirection.SHORT,
        entry, sl, tp
    ):
        return None
    return round(entry, 3), round(sl, 3), round(tp, 3)


class LiveSignalEngine:
    WEIGHTS = {"multi_timeframe": 0.20, "structure": 0.20, "liquidity": 0.15,
               "technical": 0.15, "candles": 0.10, "volatility_momentum": 0.10, "ai": 0.10}

    def __init__(self, config: Optional[Mapping[str, Any]] = None):
        self.config = dict(config or {})

    def analyze(self, frames: Mapping[str, pd.DataFrame], live_price: Optional[float] = None) -> FinalSignal:
        if not frames:
            return FinalSignal("NO TRADE", 0.0, live_price=live_price, timestamp=datetime.now(timezone.utc).isoformat(), error="No live market data.")
        prepared = {tf: _prepare(df, self.config) for tf, df in frames.items()}
        primary_tf = "M15" if "M15" in prepared else next(iter(prepared))
        primary = prepared[primary_tf]

        layers = []
        mtf = _mtf_layer(prepared); layers.append(mtf)
        st = _structure_layer(primary, self.config); layers.append(st)
        liq = _liquidity_layer(primary, self.config); layers.append(liq)
        tech = _technical_layer(primary); layers.append(tech)
        candle = _candle_layer(primary); layers.append(candle)
        vol = _volatility_layer(primary); layers.append(vol)

        # Strategy supplies an actual SMC/ICT candidate and its auditable feature vector.
        strategy = SMCConfluenceStrategy(self.config, scorer=None)
        candidates = strategy.generate_signals(primary)
        candidates = [s for s in candidates if s.direction.value in ("LONG", "SHORT")]
        candidate = candidates[-1] if candidates else None

        candidate_direction = "BUY" if candidate and candidate.direction.value == "LONG" else "SELL" if candidate else "NONE"
        features = candidate.metadata.get("features", {}) if candidate else {}
        ai = _ai_layer(features, self.config.get("ml", {}).get("model_path", "models/signal_scorer_ensemble.joblib"), candidate_direction) if candidate else LayerScore("ai", 0.0, "NONE", {"active": False, "reason": "no SMC candidate"})
        layers.append(ai)

        layer_map = {x.name: x for x in layers}
        active_ai = bool(ai.details.get("active"))
        # AI is confirmation only: when unavailable, it contributes no points rather than fake confidence.
        weights = dict(self.WEIGHTS)
        if not active_ai:
            non_ai = {k: v for k, v in weights.items() if k != "ai"}
            s = sum(non_ai.values())
            weights = {k: (v / s if k != "ai" else 0.0) for k, v in weights.items()}

        votes = []
        weighted_score = 0.0
        for name, w in weights.items():
            layer = layer_map[name]
            weighted_score += w * layer.score
            if layer.direction in ("BUY", "SELL"):
                votes.append((name, layer.direction, w))

        buy_weight = sum(w for _, d, w in votes if d == "BUY")
        sell_weight = sum(w for _, d, w in votes if d == "SELL")
        dominant = "BUY" if buy_weight > sell_weight else "SELL" if sell_weight > buy_weight else "NONE"

        # Strong structural/SMC candidate is mandatory for a trade.
        if candidate is None:
            return FinalSignal("NO TRADE", round(weighted_score, 1), live_price=live_price, timestamp=datetime.now(timezone.utc).isoformat(),
                               layers={k: {"score": v.score, "direction": v.direction, **v.details} for k,v in layer_map.items()},
                               reasons=["No validated SMC/ICT entry candidate on the primary timeframe."],
                               ai_active=active_ai)

        if dominant != candidate_direction:
            return FinalSignal("NO TRADE", round(weighted_score, 1), live_price=live_price, timestamp=datetime.now(timezone.utc).isoformat(),
                               layers={k: {"score": v.score, "direction": v.direction, **v.details} for k,v in layer_map.items()},
                               reasons=["Layer conflict: the multi-factor vote does not confirm the SMC candidate."],
                               ai_active=active_ai, ai_probability=ai.details.get("probability"))

        # AI, when available, must agree with the candidate.
        if active_ai and ai.direction != candidate_direction:
            return FinalSignal("NO TRADE", round(weighted_score, 1), live_price=live_price, timestamp=datetime.now(timezone.utc).isoformat(),
                               layers={k: {"score": v.score, "direction": v.direction, **v.details} for k,v in layer_map.items()},
                               reasons=["AI confirmation conflicts with the rule-based SMC candidate."],
                               ai_active=True, ai_probability=ai.details.get("probability"))

        confidence = round(_clip(weighted_score), 1)
        if confidence < 65.0:
            return FinalSignal("NO TRADE", confidence, live_price=live_price, timestamp=datetime.now(timezone.utc).isoformat(),
                               layers={k: {"score": v.score, "direction": v.direction, **v.details} for k,v in layer_map.items()},
                               reasons=["Signal score is below the minimum trade threshold."],
                               ai_active=active_ai, ai_probability=ai.details.get("probability"))

        # Entry is current live quote when available; otherwise latest closed candle.
        entry = float(live_price) if live_price and live_price > 0 else float(primary["close"].iloc[-1])
        atr = float(primary["atr"].iloc[-1])
        zone_top = float(candidate.metadata.get("zone_top", entry))
        zone_bottom = float(candidate.metadata.get("zone_bottom", entry))
        rr_target = float(self.config.get("risk", {}).get("reward_risk_ratio", 2.0))
        levels = _levels(candidate_direction, entry, atr, zone_top, zone_bottom, rr_target)
        if levels is None:
            return FinalSignal("NO TRADE", confidence, live_price=live_price, timestamp=datetime.now(timezone.utc).isoformat(),
                               layers={k: {"score": v.score, "direction": v.direction, **v.details} for k,v in layer_map.items()},
                               reasons=["Entry/SL/TP geometry failed validation."],
                               ai_active=active_ai, ai_probability=ai.details.get("probability"))
        entry, sl, tp = levels
        rr = abs(tp-entry) / abs(entry-sl)
        reasons = list(candidate.reasons[-6:])
        reasons.append(f"Final multi-layer score: {confidence:.1f}/100")
        return FinalSignal(candidate_direction, confidence, entry, sl, tp, round(rr, 2), live_price,
                           datetime.now(timezone.utc).isoformat(),
                           {k: {"score": round(v.score,1), "direction": v.direction, **v.details} for k,v in layer_map.items()},
                           reasons, active_ai, ai.details.get("probability"))
