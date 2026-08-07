import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.phase4.feature_pipeline import FeaturePipeline
from src.phase4.smc_engine import SmcEngine
from src.phase4.ai_engine import AiEngine
from src.phase4.signal_engine_v4 import SignalEngineV4
from src.phase4.exit_engine_v4 import ExitEngineV4
from src.phase4.portfolio_engine import PortfolioEngine
from src.phase4.execution_engine import ExecutionEngine
from src.phase4.realtime_engine import RealtimeEngine
from src.phase4.validation_engine import ValidationEngine
from src.phase4.analytics_engine import AnalyticsEngine
from src.phase4.news_engine import NewsEngine
from src.phase4.regime_engine_v4 import RegimeEngineV4


def test_phase4_engines_are_deterministic_and_no_data_is_created():
    series=[100,101,100.5,102,103,102.5,104]
    classes=[FeaturePipeline,SmcEngine,AiEngine,SignalEngineV4,ExitEngineV4,
             PortfolioEngine,ExecutionEngine,RealtimeEngine,ValidationEngine,
             AnalyticsEngine,NewsEngine,RegimeEngineV4]
    for cls in classes:
        engine=cls()
        result=engine.feature_000(series[-1], series[0]) if cls is FeaturePipeline else engine.structure_000(series[-1], series[0]) if cls is SmcEngine else engine.score_000(series[-1], series[0]) if cls is AiEngine else engine.signal_000(series[-1], series[0]) if cls is SignalEngineV4 else engine.exit_000(series[-1], series[0]) if cls is ExitEngineV4 else engine.risk_000(series[-1], series[0]) if cls is PortfolioEngine else engine.exec_000(series[-1], series[0]) if cls is ExecutionEngine else engine.stream_000(series[-1], series[0]) if cls is RealtimeEngine else engine.check_000(series[-1], series[0]) if cls is ValidationEngine else engine.metric_000(series[-1], series[0]) if cls is AnalyticsEngine else engine.news_000(series[-1], series[0]) if cls is NewsEngine else engine.regime_000(series[-1], series[0])
        assert result.ok
        assert 0 <= result.score <= 1
        assert result.values["value"] == series[-1]


def test_phase4_batch_and_state():
    engine=SignalEngineV4()
    batch=engine.batch_01([1,2,3,4])
    assert len(batch)==4
    engine.state_00("mode","research")
    assert engine.state_00("mode") == "research"
    snap=engine.snapshot()
    assert snap["history"] == 4


def test_phase4_series_methods_use_only_supplied_values():
    engine=RegimeEngineV4()
    result=engine.regime_trend_00([1,2,3,4,5],window=3)
    assert result.ok
    assert result.values["count"] == 3
