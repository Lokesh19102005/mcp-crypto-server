import pytest
from fastapi.testclient import TestClient
from app.main import app
import asyncio
import types

@pytest.fixture(autouse=True)
def stub_exchange(monkeypatch):
    class Dummy:
        async def startup(self): pass
        async def shutdown(self): pass
        async def fetch_ticker(self, exchange, symbol):
            return {"timestamp": 1234567890, "bid": 100, "ask":101, "last":100.5, "info": {}}
        async def fetch_ohlcv(self, exchange, symbol, timeframe="1m", since=None, limit=10):
            return [[1234567890, 99, 101, 98, 100.5, 10]]
    dummy = Dummy()
    # monkeypatch the app state after startup
    app.state.exchange = dummy
    yield

def test_get_ticker():
    client = TestClient(app)
    r = client.get("/api/ticker/binance/BTC/USDT")
    # route expects symbol = "BTC/USDT". test passes when route is correct
    assert r.status_code == 200
    j = r.json()
    assert j["last"] == 100.5

def test_historical():
    client = TestClient(app)
    payload = {"exchange":"binance", "symbol":"BTC/USDT", "timeframe":"1m", "limit":1}
    r = client.post("/api/historical", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert j["data"][0]["close"] == 100.5
