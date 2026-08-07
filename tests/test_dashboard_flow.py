import pandas as pd
import streamlit_app as app

def test_wait_without_data():
    sig, err = app.compute_final_signal(None)
    assert sig is None
    assert err

def test_final_signal_geometry():
    n = 80
    x = pd.Series([100 + i*0.15 for i in range(n)])
    df = pd.DataFrame({
        "open": x - 0.05,
        "high": x + 0.2,
        "low": x - 0.2,
        "close": x,
    })
    sig, err = app.compute_final_signal(df)
    assert err is None
    if sig["status"] != "WAIT":
        assert sig["sl"] < sig["entry"] < sig["tp"]
        assert sig["rr"] >= 1.0
