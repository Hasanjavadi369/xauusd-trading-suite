from src.phase5.backtest import run_next_bar

def test_next_bar_no_lookahead():
    candles=[type('C',(),{'open':100+i,'close':101+i}) for i in range(5)]
    r=run_next_bar(candles,["BUY",None,None,None,None]); assert len(r.trades)==1; assert r.trades[0].entry==101
