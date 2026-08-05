"""
موتور سیگنال ترکیبی (Confluence Engine).

منطق کلی:
1. ساختار بازار (BOS/CHOCH) جهت کلی روند را مشخص می‌کند.
2. نواحی SMC (Order Block, FVG, Supply/Demand, Liquidity) نقاط ورود بالقوه می‌دهند.
3. الگوهای کندلی و اندیکاتورها (RSI, MACD, SuperTrend, ADX, Bollinger) به‌عنوان
   فیلتر تأییدی برای افزایش/کاهش امتیاز اطمینان (confidence) استفاده می‌شوند.
4. SL بر اساس ATR و لبه‌ی ناحیه SMC، TP بر اساس Risk/Reward هدف در config تعیین می‌شود.

خروجی نهایی: لیستی از Signal با entry/SL/TP/confidence/reasons.
"""
from typing import List
import pandas as pd

from ..core.data_models import Signal, TradeDirection, SignalSource
from ..smc import structure, order_blocks, fvg as fvg_mod, liquidity, supply_demand
from ..price_action import candlestick_patterns, support_resistance
from .base_strategy import BaseStrategy


class SMCConfluenceStrategy(BaseStrategy):
    name = "SMC_ICT_Confluence"

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

            if ctx["trend"] == ("up" if is_bullish else "down"):
                confidence += 15
                reasons.append("هم‌راستا با روند غالب ساختار بازار (BOS/CHOCH)")
                sources.append(SignalSource.BOS if is_bullish else SignalSource.CHOCH)

            # همپوشانی با FVG هم‌جهت
            for fz in ctx["fvgs"]:
                same_dir = (fz.kind == "fvg_bullish") == is_bullish
                if same_dir and not (fz.top < zone.bottom or fz.bottom > zone.top):
                    confidence += 15
                    reasons.append("همپوشانی با Fair Value Gap هم‌جهت")
                    sources.append(SignalSource.FVG)
                    break

            # تایید کندلی نزدیک ناحیه
            row = df.iloc[idx]
            if is_bullish and row.get("pattern_bullish_pin") or row.get("pattern_bullish_engulfing"):
                confidence += 10
                reasons.append("تایید الگوی کندلی صعودی")
                sources.append(SignalSource.CANDLESTICK_PATTERN)
            if (not is_bullish) and (row.get("pattern_bearish_pin") or row.get("pattern_bearish_engulfing")):
                confidence += 10
                reasons.append("تایید الگوی کندلی نزولی")
                sources.append(SignalSource.CANDLESTICK_PATTERN)

            # فیلتر اندیکاتوری: RSI و SuperTrend
            if "rsi" in df.columns:
                rsi_val = row.get("rsi", 50)
                if is_bullish and rsi_val < 45:
                    confidence += 5
                    reasons.append(f"RSI ({rsi_val:.1f}) در ناحیه اشباع فروش/خنثی")
                    sources.append(SignalSource.INDICATOR_CONFLUENCE)
                if (not is_bullish) and rsi_val > 55:
                    confidence += 5
                    reasons.append(f"RSI ({rsi_val:.1f}) در ناحیه اشباع خرید/خنثی")
                    sources.append(SignalSource.INDICATOR_CONFLUENCE)

            if "supertrend_direction" in df.columns:
                st_dir = row.get("supertrend_direction", 0)
                if (is_bullish and st_dir == 1) or ((not is_bullish) and st_dir == -1):
                    confidence += 10
                    reasons.append("جهت SuperTrend هم‌راستا با سیگنال")
                    sources.append(SignalSource.INDICATOR_CONFLUENCE)

            confidence = min(confidence, 100.0)

            entry_price = zone.top if is_bullish else zone.bottom
            atr_val = row.get("atr", (zone.top - zone.bottom))
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

            signals.append(Signal(
                timestamp=df["time"].iloc[idx],
                direction=direction,
                entry_price=round(entry_price, 3),
                stop_loss=round(stop_loss, 3),
                take_profit=round(take_profit, 3),
                confidence=confidence,
                sources=sources,
                reasons=reasons,
                metadata={"zone_kind": zone.kind, "zone_top": zone.top, "zone_bottom": zone.bottom},
            ))

        signals.sort(key=lambda s: s.timestamp)
        return signals
