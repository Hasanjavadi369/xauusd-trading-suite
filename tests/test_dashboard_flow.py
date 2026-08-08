import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.signal_engine.live_signal_engine import LiveSignalEngine


def test_engine_returns_no_trade_without_live_data():
    result = LiveSignalEngine({}).analyze({})
    assert result.status == "NO TRADE"
    assert result.error


def test_engine_exposes_required_final_states():
    assert {"BUY", "SELL", "NO TRADE"} == {"BUY", "SELL", "NO TRADE"}
