"""
موتور سیگنال ترکیبی (Confluence Engine).

منطق کلی:
1. ساختار بازار (BOS/CHOCH) جهت کلی روند را مشخص می‌کند.
2. نواحی SMC (Order Block, FVG, Supply/Demand, Liquidity) نقاط ورود بالقوه می‌دهند.
3. الگوهای کندلی و اندیکاتورها (RSI, MACD, SuperTrend, ADX, Bollinger) به‌عنوان
   فیلتر تأییدی برای افزایش/کاهش امتیاز اطمینان (confidence) استفاده می‌شوند.
4. SL بر اساس ATR و لبه‌ی ناحیه SMC، TP بر اساس Risk/Reward هدف در config تعیین می‌شود.
5. (اختیاری) اگر یک SignalScorer یادگیری‌ماشین (src/ml) به استراتژی داده شود،
   علاوه بر confidence قانون‌محور، یک احتمال موفقیت آماری (ml_probability) هم
   محاسبه و به سیگنال ضمیمه می‌شود. این مدل قیمت را پیش‌بینی نمی‌کند؛ فقط از
   روی همین فیچرهای قابل‌مشاهده (فاصله/قدرت OB، FVG، هم‌جهتی اندیکاتورها، ...)
   یاد می‌گیرد که تاریخاً چه ترکیبی از این فیچرها بیشتر به TP رسیده تا SL.

خروجی نهایی: لیستی از Signal با entry/SL/TP/confidence/ml_probability/reasons.
"""
from typing import List, Optional, TYPE_CHECKING
import pandas as pd

from ..core.data_models import Signal, TradeDirection, SignalSource
from ..smc import structure, order_blocks, fvg as fvg_mod, liquidity, supply_demand
from ..price_action import candlestick_patterns, support_resistance
from .base_strategy import BaseStrategy
from ..ml.features import feature_dict_to_row

if TYPE_CHECKING:
    from ..ml.scorer import SignalScorer


class SMCConfluenceStrategy(BaseStrategy):
    name = "SMC_ICT_Confluence"

    def __init__(self, config: dict, scorer: Optional["SignalScorer"] = None):
        """
        scorer: نمونه‌ی اختیاری از src.ml.scorer.SignalScorer (از قبل train شده و
            load شده). اگر داده شود، هر سیگنال یک ml_probability هم می‌گیرد.
            کاملاً اختیاری است — بدون آن، موتور دقیقاً مثل قبل (فقط قانون‌محور) کار می‌کند.
        """
        super().__init__(config)
        self.scorer = scorer

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = candlestick_patterns.detect_all_patterns(df)
        return df

    def _build_context(self, df: pd.DataFrame):
        smc_cfg = self.config.get("smc", {})
        swing_lookback = smc_cfg.get("swing_lookback", 5)

        swings = structure.find_swing_points(df, swing_lookback)
        bos_choch_events = structure.detect_bos_choch(df, swings)
        trend_dir = structure.current_trend(swings, bos_choch_events)

        obs = order_blocks.detect_order_blocks(df, smc_cfg.get("order_block_lookback", 20))
        order_blocks.mark_mitigated_zones(obs, df)

        fvgs = fvg_mod.detect_fvg(df, smc_cfg.get("fvg_min_gap_pct", 0.02))
        fvg_mod.mark_filled_fvgs(fvgs, df)

        sd_zones = supply_demand.detect_supply_demand_zones(df)
        liq_zones = liquidity.detect_equal_levels(swings, smc_cfg.get("liquidity_equal_tolerance_pct", 0.03))
        sweeps = liquidity.detect_liquidity_sweep(df, liq_zones)
        sr_zones = support_resistance.detect_support_resistance(swings)

        return {
            "swings": swings, "bos_choch": bos_choch_events, "trend": trend_dir,
            "order_blocks": obs, "fvgs": fvgs, "supply_demand": sd_zones,
            "liquidity_zones": liq_zones, "sweeps": sweeps, "support_resistance": sr_zones,
        }

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        ctx = self._build_context(df)
        signals: List[Signal] = []
        rr_target = self.config.get("risk", {}).get("reward_risk_ratio", 2.0)

        active_obs = [z for z in ctx["order_blocks"] if not z.mitigated]

        for zone in active_obs:
            end_idx_series = df[df["time"] == zone.end_time].index
            if len(end_idx_series) == 0:
                continue
            idx = end_idx_series[0]
            if idx + 1 >= len(df):
                continue

            is_bullish = zone.kind == "order_block_bullish"
            # جهت باید هم‌راستا با روند کلی (trend) از ساختار بازار باشد
            if is_bullish and ctx["trend"] not in ("up", "unknown"):
                continue
            if not is_bullish and ctx["trend"] not in ("down", "unknown"):
                continue

            confidence = 40.0
            reasons = [f"Order Block {'صعودی' if is_bullish else 'نزولی'} شناسایی شد"]
            sources = [SignalSource.ORDER_BLOCK]
            row = df.iloc[idx]
            atr_val = row.get("atr", (zone.top - zone.bottom))
            if not atr_val or pd.isna(atr_val) or atr_val == 0:
                atr_val = max(zone.top - zone.bottom, 1e-6)

            # --- فیچرهای پایه (همیشه محاسبه می‌شوند، چه scorer باشد چه نباشد) ---
            features = {
                "ob_strength": float(zone.strength),
                "ob_width_atr": float((zone.top - zone.bottom) / atr_val),
                "trend_aligned": 0.0,
                "fvg_confluence": 0.0,
                "fvg_strength": 0.0,
                "candle_confirmation": 0.0,
                "rsi_value": float(row.get("rsi", 50.0)) if not pd.isna(row.get("rsi", 50.0)) else 50.0,
                "rsi_confirmation": 0.0,
                "supertrend_aligned": 0.0,
                "adx_value": float(row.get("adx", 0.0)) if not pd.isna(row.get("adx", 0.0)) else 0.0,
                "macd_hist": float(row.get("macd_hist", 0.0)) if not pd.isna(row.get("macd_hist", 0.0)) else 0.0,
                "bb_position": 0.5,
                "atr_pct": float(atr_val / row["close"]) if row["close"] else 0.0,
                "liquidity_sweep_nearby": 0.0,
                "sr_confluence": 0.0,
                "n_confluences": 0.0,
                "risk_reward": float(rr_target),
                "rule_confidence": 0.0,  # در پایان پر می‌شود
            }

            if "bb_upper" in df.columns and "bb_lower" in df.columns:
                bb_upper, bb_lower = row.get("bb_upper"), row.get("bb_lower")
                if bb_upper is not None and bb_lower is not None and not pd.isna(bb_upper) and not pd.isna(bb_lower) and (bb_upper - bb_lower) != 0:
                    features["bb_position"] = float((row["close"] - bb_lower) / (bb_upper - bb_lower))

            if ctx["trend"] == ("up" if is_bullish else "down"):
                confidence += 15
                reasons.append("هم‌راستا با روند غالب ساختار بازار (BOS/CHOCH)")
                sources.append(SignalSource.BOS if is_bullish else SignalSource.CHOCH)
                features["trend_aligned"] = 1.0

            # همپوشانی با FVG هم‌جهت
            for fz in ctx["fvgs"]:
                same_dir = (fz.kind == "fvg_bullish") == is_bullish
                if same_dir and not (fz.top < zone.bottom or fz.bottom > zone.top):
                    confidence += 15
                    reasons.append("همپوشانی با Fair Value Gap هم‌جهت")
                    sources.append(SignalSource.FVG)
                    features["fvg_confluence"] = 1.0
                    features["fvg_strength"] = max(features["fvg_strength"], float(fz.strength))
                    break

            # تایید کندلی نزدیک ناحیه
            if is_bullish and row.get("pattern_bullish_pin") or row.get("pattern_bullish_engulfing"):
                confidence += 10
                reasons.append("تایید الگوی کندلی صعودی")
                sources.append(SignalSource.CANDLESTICK_PATTERN)
                features["candle_confirmation"] = 1.0
            if (not is_bullish) and (row.get("pattern_bearish_pin") or row.get("pattern_bearish_engulfing")):
                confidence += 10
                reasons.append("تایید الگوی کندلی نزولی")
                sources.append(SignalSource.CANDLESTICK_PATTERN)
                features["candle_confirmation"] = 1.0

            # فیلتر اندیکاتوری: RSI و SuperTrend
            if "rsi" in df.columns:
                rsi_val = row.get("rsi", 50)
                if is_bullish and rsi_val < 45:
                    confidence += 5
                    reasons.append(f"RSI ({rsi_val:.1f}) در ناحیه اشباع فروش/خنثی")
                    sources.append(SignalSource.INDICATOR_CONFLUENCE)
                    features["rsi_confirmation"] = 1.0
                if (not is_bullish) and rsi_val > 55:
                    confidence += 5
                    reasons.append(f"RSI ({rsi_val:.1f}) در ناحیه اشباع خرید/خنثی")
                    sources.append(SignalSource.INDICATOR_CONFLUENCE)
                    features["rsi_confirmation"] = 1.0

            if "supertrend_direction" in df.columns:
                st_dir = row.get("supertrend_direction", 0)
                if (is_bullish and st_dir == 1) or ((not is_bullish) and st_dir == -1):
                    confidence += 10
                    reasons.append("جهت SuperTrend هم‌راستا با سیگنال")
                    sources.append(SignalSource.INDICATOR_CONFLUENCE)
                    features["supertrend_aligned"] = 1.0

            # نزدیکی به Liquidity Sweep هم‌جهت اخیر (طی ۵۰ کندل قبل از سیگنال)
            for sweep in ctx["sweeps"]:
                sweep_idx = df[df["time"] == sweep["time"]].index
                if len(sweep_idx) == 0:
                    continue
                si = sweep_idx[0]
                if 0 <= idx - si <= 50:
                    if (is_bullish and sweep["type"] == "sweep_low") or ((not is_bullish) and sweep["type"] == "sweep_high"):
                        features["liquidity_sweep_nearby"] = 1.0
                        if SignalSource.LIQUIDITY_SWEEP not in sources:
                            sources.append(SignalSource.LIQUIDITY_SWEEP)
                            reasons.append("شکار نقدینگی (Liquidity Sweep) هم‌جهت قبل از سیگنال")
                        break

            # همپوشانی ناحیه با یک سطح حمایت/مقاومت شناخته‌شده
            for sr in ctx["support_resistance"]:
                if not (sr.top < zone.bottom or sr.bottom > zone.top):
                    features["sr_confluence"] = 1.0
                    if SignalSource.SUPPORT_RESISTANCE not in sources:
                        sources.append(SignalSource.SUPPORT_RESISTANCE)
                        reasons.append("همپوشانی با سطح حمایت/مقاومت شناخته‌شده")
                    break

            confidence = min(confidence, 100.0)
            features["n_confluences"] = float(len(sources))
            features["rule_confidence"] = float(confidence / 100.0)

            entry_price = zone.top if is_bullish else zone.bottom
            buffer = max(atr_val * 0.2, (zone.top - zone.bottom) * 0.1)

            if is_bullish:
                stop_loss = zone.bottom - buffer
                risk = entry_price - stop_loss
                take_profit = entry_price + risk * rr_target
                direction = TradeDirection.LONG
            else:
                stop_loss = zone.top + buffer
                risk = stop_loss - entry_price
                take_profit = entry_price - risk * rr_target
                direction = TradeDirection.SHORT

            if risk <= 0:
                continue

            signal = Signal(
                timestamp=df["time"].iloc[idx],
                direction=direction,
                entry_price=round(entry_price, 3),
                stop_loss=round(stop_loss, 3),
                take_profit=round(take_profit, 3),
                confidence=confidence,
                sources=sources,
                reasons=reasons,
                metadata={"zone_kind": zone.kind, "zone_top": zone.top, "zone_bottom": zone.bottom,
                          "features": features},
            )

            if self.scorer is not None:
                try:
                    proba = self.scorer.predict_proba_one(feature_dict_to_row(features))
                    signal.ml_probability = round(float(proba), 4)
                    signal.reasons.append(
                        f"امتیاز مدل یادگیری ماشین ({self.scorer.backend_name}): "
                        f"{signal.ml_probability * 100:.1f}% احتمال رسیدن به TP"
                    )
                except Exception:
                    # اگر مدل روی این ورودی شکست خورد، سیگنال قانون‌محور همچنان معتبر می‌ماند
                    signal.ml_probability = None

            signals.append(signal)

        signals.sort(key=lambda s: s.timestamp)
        return signals
