"""Phase 4 high-level orchestration facade.

The facade combines independent deterministic components while keeping the
actual market observations supplied by the caller. It is intentionally
broker-agnostic and does not place orders itself.
"""
from __future__ import annotations
from typing import Any, Mapping, Sequence
from .feature_pipeline import FeaturePipeline
from .smc_engine import SmcEngine
from .ai_engine import AiEngine
from .signal_engine_v4 import SignalEngineV4
from .exit_engine_v4 import ExitEngineV4
from .portfolio_engine import PortfolioEngine
from .execution_engine import ExecutionEngine
from .realtime_engine import RealtimeEngine
from .validation_engine import ValidationEngine
from .analytics_engine import AnalyticsEngine
from .news_engine import NewsEngine
from .regime_engine_v4 import RegimeEngineV4

class Phase4Pipeline:
    """Single entry point for Phase 4 research/live-analysis orchestration."""
    def __init__(self, config: Mapping[str, Any] | None = None) -> None:
        cfg=dict(config or {})
        self.feature=FeaturePipeline(cfg.get("feature"))
        self.smc=SmcEngine(cfg.get("smc"))
        self.ai=AiEngine(cfg.get("ai"))
        self.signal=SignalEngineV4(cfg.get("signal"))
        self.exit=ExitEngineV4(cfg.get("exit"))
        self.portfolio=PortfolioEngine(cfg.get("portfolio"))
        self.execution=ExecutionEngine(cfg.get("execution"))
        self.realtime=RealtimeEngine(cfg.get("realtime"))
        self.validation=ValidationEngine(cfg.get("validation"))
        self.analytics=AnalyticsEngine(cfg.get("analytics"))
        self.news=NewsEngine(cfg.get("news"))
        self.regime=RegimeEngineV4(cfg.get("regime"))

    def analyze(self, observations: Sequence[float]) -> dict[str, Any]:
        """Analyze caller-supplied observations without inventing prices."""
        values=list(observations)
        regime=self.regime.regime_trend_00(values)
        structure=self.smc.structure_swing_high_00(values)
        ai=self.ai.score_trend_00(values)
        signal=self.signal.signal_trend_00(values)
        return {
            "regime": regime,
            "structure": structure,
            "ai": ai,
            "signal": signal,
            "observation_count": len(values),
        }
