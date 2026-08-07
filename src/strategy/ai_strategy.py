"""
AIStrategy: استراتژی مبتنی بر مدل یادگیری ماشین (پیش‌بینی رفتار قیمت).

EnsembleStrategy: ترکیب موتور قانون‌محور SMC/ICT با مدل یادگیری ماشین —
سیگنال نهایی وقتی صادر می‌شود که هر دو موتور هم‌جهت باشند (یا طبق حالت
انتخابی کاربر، هرکدام به‌تنهایی) — این همان «شبکه‌ی ادغامی» درخواستی است:
قوانین صریح SMC + الگوی آموخته‌شده از داده، برای فیلتر کردن یکدیگر.
"""
from typing import List, Optional
import pandas as pd

from ..core.data_models import Signal, TradeDirection, SignalSource
from ..price_action import candlestick_patterns
from .base_strategy import BaseStrategy
from .signal_engine import SMCConfluenceStrategy
from ..ml.feature_engineering import build_features
from ..ml.model import MLSignalModel


class AIStrategy(BaseStrategy):
    name = "AI_PriceAction_Learner"

    def __init__(self, config: dict, model: MLSignalModel):
        super().__init__(config)
        self.model = model

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        return candlestick_patterns.detect_all_patterns(df)

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        ai_cfg = self.config.get("ai", {})
        min_conf = ai_cfg.get("min_confidence_pct", 60.0) / 100.0
        tp_mult = ai_cfg.get("tp_atr_mult", 2.0)
        sl_mult = ai_cfg.get("sl_atr_mult", 1.0)

        features = build_features(df).replace([float("inf"), float("-inf")], pd.NA)
        valid_mask = features.notna().all(axis=1)
        if valid_mask.sum() == 0:
            return []

        proba = self.model.predict_proba(features[valid_mask])

        signals: List[Signal] = []
        for idx in proba.index:
            row = df.loc[idx]
            atr_val = row.get("atr")
            if pd.isna(atr_val) or atr_val <= 0:
                continue

            p_bull = proba.loc[idx, "proba_bullish"]
            p_bear = proba.loc[idx, "proba_bearish"]
            entry = row["close"]

            if p_bull >= min_conf and p_bull > p_bear:
                signals.append(Signal(
                    timestamp=row["time"], direction=TradeDirection.LONG,
                    entry_price=round(entry, 3),
                    stop_loss=round(entry - sl_mult * atr_val, 3),
                    take_profit=round(entry + tp_mult * atr_val, 3),
                    confidence=round(p_bull * 100, 1),
                    sources=[SignalSource.INDICATOR_CONFLUENCE],
                    reasons=[f"مدل یادگیری ماشین احتمال {p_bull * 100:.1f}% برای حرکت صعودی پیش‌بینی کرد"],
                    metadata={"model": self.model.model_type, "p_bullish": float(p_bull), "p_bearish": float(p_bear)},
                ))
            elif p_bear >= min_conf and p_bear > p_bull:
                signals.append(Signal(
                    timestamp=row["time"], direction=TradeDirection.SHORT,
                    entry_price=round(entry, 3),
                    stop_loss=round(entry + sl_mult * atr_val, 3),
                    take_profit=round(entry - tp_mult * atr_val, 3),
                    confidence=round(p_bear * 100, 1),
                    sources=[SignalSource.INDICATOR_CONFLUENCE],
                    reasons=[f"مدل یادگیری ماشین احتمال {p_bear * 100:.1f}% برای حرکت نزولی پیش‌بینی کرد"],
                    metadata={"model": self.model.model_type, "p_bullish": float(p_bull), "p_bearish": float(p_bear)},
                ))

        signals.sort(key=lambda s: s.timestamp)
        return signals


class EnsembleStrategy(BaseStrategy):
    """
    ترکیب SMC/ICT (قوانین صریح) + AI (الگوی آموخته‌شده از داده).

    mode:
      "agreement" : سیگنال فقط وقتی صادر می‌شود که هر دو موتور هم‌جهت باشند
                    (کمترین تعداد سیگنال، بالاترین اطمینان)
      "any"       : سیگنال هرکدام از موتورها که معتبر باشد پذیرفته می‌شود
                    (بیشترین تعداد سیگنال)
    """
    name = "Ensemble_SMC_AI"

    def __init__(self, config: dict, model: MLSignalModel, mode: str = "agreement"):
        super().__init__(config)
        self.smc = SMCConfluenceStrategy(config)
        self.ai = AIStrategy(config, model)
        self.mode = mode

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.smc.prepare(df)
        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        smc_signals = self.smc.generate_signals(df)
        ai_signals = self.ai.generate_signals(df)

        if self.mode == "any":
            combined = smc_signals + ai_signals
            combined.sort(key=lambda s: s.timestamp)
            return combined

        # mode == "agreement": فقط سیگنال‌هایی که در بازه‌ی زمانی نزدیک هم‌جهت باشند
        agreed: List[Signal] = []
        tolerance = pd.Timedelta(hours=4)
        for smc_sig in smc_signals:
            for ai_sig in ai_signals:
                if smc_sig.direction != ai_sig.direction:
                    continue
                if abs(smc_sig.timestamp - ai_sig.timestamp) <= tolerance:
                    merged = Signal(
                        timestamp=max(smc_sig.timestamp, ai_sig.timestamp),
                        direction=smc_sig.direction,
                        entry_price=smc_sig.entry_price,
                        stop_loss=smc_sig.stop_loss,
                        take_profit=smc_sig.take_profit,
                        confidence=round((smc_sig.confidence + ai_sig.confidence) / 2 + 10, 1),
                        sources=list(set(smc_sig.sources + ai_sig.sources)),
                        reasons=smc_sig.reasons + ai_sig.reasons +
                                ["✅ تایید دوسویه: هم موتور SMC و هم مدل یادگیری ماشین هم‌جهت هستند"],
                        metadata={**smc_sig.metadata, **ai_sig.metadata},
                    )
                    merged.confidence = min(merged.confidence, 100.0)
                    agreed.append(merged)
                    break

        agreed.sort(key=lambda s: s.timestamp)
        return agreed
