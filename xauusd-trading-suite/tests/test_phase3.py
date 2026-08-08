import pandas as pd, numpy as np
from src.market.regime import detect_regime
from src.execution.guards import ExecutionConstraints, validate_execution
from src.risk_management.dynamic_exits import manage_exit

def frame(n=120, trend=1.0):
    c=1900+np.arange(n)*trend
    return pd.DataFrame({"time":pd.date_range("2026-01-01",periods=n,freq="h"),
                         "open":c,"high":c+2,"low":c-2,"close":c,"volume":100})

def test_regime_up():
    r=detect_regime(frame())
    assert r.trend=="up"

def test_execution_long():
    c=ExecutionConstraints(digits=2,point=.01,stops_level_points=10)
    x=validate_execution("LONG",2000,2000.05,1998,2005,c)
    assert x.ok and x.entry==2000.05

def test_execution_rejects_bad_long():
    c=ExecutionConstraints(digits=2,point=.01,stops_level_points=10)
    x=validate_execution("LONG",2000,2000.05,2000.04,2005,c)
    assert not x.ok

def test_dynamic_break_even_trailing():
    d=manage_exit("LONG",2000,2005,1997,2,rr_trigger=1,atr_trail=1)
    assert d.action=="modify_stop" and d.new_stop>1997
