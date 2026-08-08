from src.risk_management.position_sizing import SymbolSpec, calculate_position_size, risk_reward_ratio
from src.risk_management.trade_manager import RiskConfig, TradeManager
from src.core.data_models import Trade, TradeDirection
from src.backtest.metrics import compute_performance


def test_calculate_position_size_respects_risk_amount():
    spec = SymbolSpec(contract_size=100, tick_size=0.01, tick_value=1.0)
    volume = calculate_position_size(
        account_balance=10_000, risk_percent=1.0,
        entry_price=2000.0, stop_loss=1995.0, symbol_spec=spec,
    )
    assert spec.volume_min <= volume <= spec.volume_max


def test_calculate_position_size_zero_distance_returns_min_lot():
    spec = SymbolSpec()
    volume = calculate_position_size(10_000, 1.0, 2000.0, 2000.0, spec)
    assert volume == spec.volume_min


def test_risk_reward_ratio():
    assert risk_reward_ratio(2000, 1990, 2020) == 2.0
    assert risk_reward_ratio(2000, 2000, 2020) == 0.0


def _make_trade(entry=2000.0, sl=1990.0, tp=2020.0, direction=TradeDirection.LONG):
    return Trade(
        id="t1", symbol="XAUUSD", direction=direction, volume=0.1,
        entry_price=entry, stop_loss=sl, take_profit=tp, open_time="2024-01-01",
    )


def test_break_even_moves_stop_to_entry():
    tm = TradeManager(RiskConfig(break_even_trigger_rr=1.0))
    trade = _make_trade()
    trade = tm.apply_break_even(trade, current_price=2010.0)  # RR = 1.0
    assert trade.stop_loss == trade.entry_price
    assert trade.break_even_applied is True


def test_break_even_not_triggered_before_target_rr():
    tm = TradeManager(RiskConfig(break_even_trigger_rr=1.0))
    trade = _make_trade()
    trade = tm.apply_break_even(trade, current_price=2003.0)  # RR = 0.3
    assert trade.stop_loss == 1990.0
    assert trade.break_even_applied is False


def test_trailing_stop_moves_up_for_long():
    tm = TradeManager(RiskConfig(trailing_start_rr=1.0, trailing_distance_atr_mult=1.0))
    trade = _make_trade()
    trade = tm.apply_trailing_stop(trade, current_price=2015.0, atr_value=2.0)
    assert trade.stop_loss == 2013.0
    assert trade.trailing_stop_active is True


def test_compute_performance_empty_trades():
    report = compute_performance([], initial_balance=10_000)
    assert report.total_trades == 0
    assert report.win_rate == 0.0


def test_compute_performance_win_rate_and_profit_factor():
    trades = []
    for i, profit in enumerate([100, -50, 200, -30]):
        t = _make_trade()
        t.is_open = False
        t.profit = profit
        t.close_time = f"2024-01-0{i + 1}"
        trades.append(t)
    report = compute_performance(trades, initial_balance=10_000)
    assert report.total_trades == 4
    assert report.winning_trades == 2
    assert report.win_rate == 50.0
    assert report.net_profit == 220
    assert report.profit_factor == round(300 / 80, 2)


def test_trade_levels_are_consistent_with_market_entry_long():
    from src.risk_management.levels import build_levels, validate_levels
    levels = build_levels(TradeDirection.LONG, 2400.0, 10.0, 2395.0, 2388.0, rr_target=2.5)
    assert levels is not None
    assert levels.stop_loss < levels.entry < levels.take_profit
    assert round((levels.take_profit - levels.entry) / (levels.entry - levels.stop_loss), 2) == 2.5
    assert validate_levels(TradeDirection.LONG, levels.entry, levels.stop_loss, levels.take_profit)


def test_trade_levels_are_consistent_with_market_entry_short():
    from src.risk_management.levels import build_levels, validate_levels
    levels = build_levels(TradeDirection.SHORT, 2400.0, 10.0, 2412.0, 2405.0, rr_target=2.0)
    assert levels is not None
    assert levels.take_profit < levels.entry < levels.stop_loss
    assert round((levels.entry - levels.take_profit) / (levels.stop_loss - levels.entry), 2) == 2.0
    assert validate_levels(TradeDirection.SHORT, levels.entry, levels.stop_loss, levels.take_profit)


def test_structural_target_caps_to_nearest_valid_long_resistance():
    from src.risk_management.levels import select_structural_target
    tp = select_structural_target(TradeDirection.LONG, 2000.0, 10.0, 2.0, [2015.0, 2025.0, 2050.0])
    assert tp == 2025.0


def test_structural_target_caps_to_nearest_valid_short_support():
    from src.risk_management.levels import select_structural_target
    tp = select_structural_target(TradeDirection.SHORT, 2000.0, 10.0, 2.0, [1985.0, 1975.0, 1950.0])
    assert tp == 1975.0
