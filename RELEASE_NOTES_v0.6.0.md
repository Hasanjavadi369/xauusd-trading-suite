# XAUUSD Trading Suite v0.6.0 — Focused Live Signal Engine

## New architecture

`LIVE XAUUSD → Multi-Timeframe → Trend/Structure → Liquidity/SMC/ICT → Candlestick/Technical → Volatility/Momentum → AI Confirmation → Signal Scoring → BUY/SELL/NO TRADE → Entry/SL/TP`

### Changes
- Replaced the previous single EMA/ATR final-signal logic with `src/signal_engine/live_signal_engine.py`.
- Live analysis uses M5, M15, H1, H4 and D1 real candles.
- Market structure includes swing/BOS/CHOCH context.
- Liquidity layer includes equal highs/lows and liquidity sweeps.
- SMC candidate generation uses Order Blocks and FVG confluence from the existing strategy engine.
- Technical layer uses EMA, RSI, MACD and ADX.
- Candlestick confirmation uses the existing price-action detector.
- Volatility/momentum layer uses ATR and ADX.
- AI is a confirmation layer only and is active only when a trained real-data ensemble model exists.
- Final decision can be `BUY`, `SELL`, or `NO TRADE`.
- Entry uses the current live quote when available.
- SL/TP are recalculated from the current price, ATR and SMC zone and validated before display.
- Dashboard was simplified to focus on live price, final signal, Entry, SL, TP and R:R.
- No synthetic market prices are generated.

## Important
A trained AI model is intentionally not fabricated or bundled. To activate the AI layer, train `signal_scorer_ensemble.joblib` only on real historical market data.
