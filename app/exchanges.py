import ccxt.async_support as ccxt
import asyncio
from typing import Dict, Any, List, Optional
from .cache import InMemoryCache

DEFAULT_EXCHANGES = ["binance", "kraken", "coinbase"]

class ExchangeClient:
    def __init__(self, exchanges: Optional[List[str]] = None):
        self.exchanges = exchanges or DEFAULT_EXCHANGES
        self._clients: Dict[str, ccxt.Exchange] = {}
        self.cache = InMemoryCache(ttl=5)

    async def startup(self):
        for name in self.exchanges:
            klass = getattr(ccxt, name)
            client = klass({"enableRateLimit": True})
            self._clients[name] = client
        # optionally test connections

    async def shutdown(self):
        for client in self._clients.values():
            try:
                await client.close()
            except Exception:
                pass

    def _cache_key(self, method: str, *args, **kwargs):
        return f"{method}:" + ":".join(map(str, args)) + ":" + ",".join(f"{k}={v}" for k,v in kwargs.items())

    async def fetch_ticker(self, exchange: str, symbol: str) -> Dict[str, Any]:
        key = self._cache_key("ticker", exchange, symbol)
        cached = await self.cache.get(key)
        if cached:
            return cached
        client = self._clients.get(exchange)
        if not client:
            raise ValueError(f"Unsupported exchange: {exchange}")
        try:
            ticker = await client.fetch_ticker(symbol)
            await self.cache.set(key, ticker)
            return ticker
        except Exception as e:
            raise

    async def fetch_ohlcv(self, exchange: str, symbol: str, timeframe: str = "1m", since: Optional[int]=None, limit: int = 100):
        key = self._cache_key("ohlcv", exchange, symbol, timeframe, since, limit)
        cached = await self.cache.get(key)
        if cached:
            return cached
        client = self._clients.get(exchange)
        if not client:
            raise ValueError(f"Unsupported exchange: {exchange}")
        try:
            ohlcv = await client.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
            # normalize to list of dicts
            await self.cache.set(key, ohlcv)
            return ohlcv
        except Exception as e:
            raise
