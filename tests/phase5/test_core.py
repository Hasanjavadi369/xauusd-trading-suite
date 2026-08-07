import pytest
from src.phase5 import *

def rows(n=60):
    out=[]; p=2300.0
    for i in range(n):
        o=p; c=p+0.5; h=c+0.3; l=o-0.2; out.append({'timestamp':i,'open':o,'high':h,'low':l,'close':c,'volume':100}); p=c
    return out

def test_validation_and_snapshot():
    r=rows(); assert validate_ohlcv(r).valid; s=snapshot(clean_candles(r)); assert s.price>0 and s.atr>0

def test_plan_geometry():
    s=snapshot(clean_candles(rows())); plan=build_trade_plan(s,'BUY',BrokerRules(digits=2,point=.01),2.0,1.5); assert plan.valid; assert plan.stop_loss<plan.entry<plan.take_profit and plan.rr>=2

def test_risk_size():
    p=size_position(10000,2300,2290,100); assert p.valid and p.lots>0 and p.risk_fraction<=.01

def test_leakage():
    with pytest.raises(ValueError): assert_no_future_features([2],[1])
