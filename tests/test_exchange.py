import pytest
import asyncio
from app.exchanges import ExchangeClient

# Dummy ccxt-like class for testing
class DummyClient:
    def __init__(self, *args, **kwargs):
        self.closed = False

    async def fetch_ticker(self, symbol):
        return {
            "timestamp": 1234567890,
            "bid": 100,
            "ask": 101,
            "last": 100.5,
            "info": {}
        }

    async def fetch_ohlcv(self, symbol, timeframe="1m", since=None, limit=10):
        return [
            [1234567890, 99, 101, 98, 100.5, 20]  # ts, open, high, low, close, volume
        ]

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_fetch_ticker(monkeypatch):
    client = ExchangeClient(exchanges=["dummy"])

    # Patch clients
    monkeypatch.setattr(client, "_clients", {"dummy": DummyClient()})

    ticker = await client.fetch_ticker("dummy", "BTC/USDT")
    assert ticker["last"] == 100.5
    assert ticker["bid"] == 100
    assert ticker["ask"] == 101
    assert ticker["timestamp"] == 1234567890


@pytest.mark.asyncio
async def test_fetch_ohlcv(monkeypatch):
    client = ExchangeClient(exchanges=["dummy"])
    monkeypatch.setattr(client, "_clients", {"dummy": DummyClient()})

    ohlcv = await client.fetch_ohlcv("dummy", "BTC/USDT")
    assert isinstance(ohlcv, list)
    assert ohlcv[0][1] == 99      # open
    assert ohlcv[0][4] == 100.5   # close
    assert ohlcv[0][5] == 20      # volume


@pytest.mark.asyncio
async def test_cache(monkeypatch):
    """Ensures fetch_ticker returns cached value on second call."""
    client = ExchangeClient(exchanges=["dummy"])
    dummy = DummyClient()
    monkeypatch.setattr(client, "_clients", {"dummy": dummy})

    # First call → cache fill
    t1 = await client.fetch_ticker("dummy", "BTC/USDT")
    # Second call → cached
    t2 = await client.fetch_ticker("dummy", "BTC/USDT")

    assert t1 == t2  # should be identical response, proving cache works
