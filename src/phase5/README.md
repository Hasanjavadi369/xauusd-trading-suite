# Phase 5 — Quality & Quant Reliability

Phase 5 prioritizes correctness over code volume. It adds a small, deterministic
quantitative core that can be used by the live dashboard, research scripts and
future MT5 adapter.

## Safety properties
- No generated market prices.
- OHLC geometry is validated before analysis.
- Timestamps can be checked for monotonicity.
- Explicit future-feature leakage assertion.
- TP/SL geometry is direction-safe and broker-aware.
- Position sizing is capped by an explicit risk budget.
- Backtests enter on the next bar rather than the signal bar close.
- Spread and commission are explicit costs.

## Main API
`Phase5Engine.analyze(rows, side=None, equity=None, value_per_price_unit=1.0)`

The engine returns validation status, market snapshot, trade plan and optional
position size. It does not submit broker orders.
