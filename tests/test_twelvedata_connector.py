import os
import requests

from src.connectors.twelvedata_connector import (
    fetch_time_series, get_api_key, TwelveDataError,
)


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_get_api_key_raises_without_source():
    os.environ.pop("TWELVEDATA_API_KEY", None)
    try:
        get_api_key()
        assert False, "باید خطا می‌داد"
    except TwelveDataError:
        pass


def test_get_api_key_prefers_explicit_over_env():
    os.environ["TWELVEDATA_API_KEY"] = "env_key"
    assert get_api_key("explicit_key") == "explicit_key"
    assert get_api_key() == "env_key"
    del os.environ["TWELVEDATA_API_KEY"]


def test_fetch_time_series_parses_and_sorts_ascending(monkeypatch):
    payload = {
        "status": "ok",
        "values": [
            {"datetime": "2024-01-01 02:00:00", "open": "10", "high": "11", "low": "9", "close": "10.5"},
            {"datetime": "2024-01-01 00:00:00", "open": "8", "high": "9", "low": "7", "close": "8.5"},
            {"datetime": "2024-01-01 01:00:00", "open": "8.5", "high": "10", "low": "8", "close": "9.5"},
        ],
    }
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(payload))

    df = fetch_time_series(symbol="XAU/USD", interval="H1", outputsize=3, api_key="fake")

    assert list(df.columns) == ["time", "open", "high", "low", "close", "volume"]
    assert list(df["close"]) == [8.5, 9.5, 10.5]
    assert df["time"].is_monotonic_increasing


def test_fetch_time_series_raises_on_error_payload(monkeypatch):
    payload = {"status": "error", "message": "invalid apikey"}
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(payload))

    try:
        fetch_time_series(symbol="XAU/USD", api_key="bad_key")
        assert False, "باید TwelveDataError می‌داد"
    except TwelveDataError as e:
        assert "invalid apikey" in str(e)
