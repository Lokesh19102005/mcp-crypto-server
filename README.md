# MCP Crypto Server (Python) — 

## Overview
This project implements a minimal MCP-style server to fetch real-time and historical cryptocurrency data from major exchanges using `ccxt` (async). It provides:
- HTTP endpoints for ticker and historical OHLCV
- WebSocket endpoint for pushing real-time updates
- Caching (in-memory) to reduce rate-limit hits
- Robust error handling and tests

## How to run (local)
1. Clone repo
2. Create virtualenv:
   python -m venv venv && source venv/bin/activate
3. Install:
   pip install -r requirements.txt
4. Start server:
   uvicorn app.main:app --reload --port 8000
 
Notes for Windows PowerShell:
```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Endpoints
- `GET /api/ticker/{exchange}/{symbol}`  
  Example: `GET /api/ticker/binance/BTC/USDT`  
- `POST /api/historical`  
  Body: `{ "exchange": "binance", "symbol":"BTC/USDT", "timeframe":"1m", "limit":100 }`  
- `WS /ws` - simple websocket for real-time pushes

Examples
--------
Get current ticker for BTC/USDT on Binance:

```powershell
Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/ticker/binance/BTC/USDT"
```

Fetch historical OHLCV data (1m candles):

```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/historical" -ContentType "application/json" -Body '{"exchange":"binance","symbol":"BTC/USDT","timeframe":"1m","limit":10}'
```

WebSocket usage
---------------
The WebSocket endpoint at `/ws` provides a connection manager and broadcast helper. By default the server accepts connections and will echo/forward messages, but it does not yet run a background producer that polls exchanges and pushes live market updates. You can connect with any websocket client (e.g., `wscat`, browser) to send/receive messages.

## Tests
Run:

## Notes & assumptions
- Symbols must be provided in exchange-specific format (e.g., `BTC/USDT`).
- `ccxt` rate limits are obeyed by `enableRateLimit=True`. For production, use exchange-specific API keys, retry/backoff, and Redis for caching.
- Real-time streaming is implemented as a WebSocket manager; for production, create background tasks polling exchanges or use exchange user-data streams where available.

Tests
-----
Run the full test-suite with:

```powershell
python -m pytest -v
```
What I changed / notes
----------------------
- Registered the project's `ValueError` -> 400 JSON handler so API errors produced as `ValueError` return a clean 400 response.

Assumptions
-----------
- Symbols use exchange-specific format (e.g. `BTC/USDT`).
- The in-memory cache is small and intended for demo/testing; a Redis-backed cache is recommended for production loads.
