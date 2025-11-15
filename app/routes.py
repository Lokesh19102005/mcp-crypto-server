from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List
from .schema import TickerResponse, HistoricalRequest, HistoricalResponse, HistoricalPoint
from .exchanges import ExchangeClient

router = APIRouter()

# get exchange client from app state
def get_exchange_client(request: Request) -> ExchangeClient:
    return request.app.state.exchange

@router.get("/ticker/{exchange}/{symbol:path}", response_model=TickerResponse)
async def get_ticker(exchange: str, symbol: str, request: Request):
    client = get_exchange_client(request)
    try:
        ticker = await client.fetch_ticker(exchange, symbol)
        return {
            "exchange": exchange,
            "symbol": symbol,
            "timestamp": int(ticker.get("timestamp") or 0),
            "bid": ticker.get("bid"),
            "ask": ticker.get("ask"),
            "last": ticker.get("last"),
            "info": ticker.get("info") or ticker
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail="Upstream exchange error")

@router.post("/historical", response_model=HistoricalResponse)
async def get_historical(req: HistoricalRequest, request: Request):
    client = get_exchange_client(request)
    try:
        raw = await client.fetch_ohlcv(req.exchange, req.symbol, timeframe=req.timeframe, since=req.since, limit=req.limit)
        # ccxt returns list of lists: [timestamp, open, high, low, close, volume]
        data = [
            HistoricalPoint(
                timestamp=int(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]) if len(row) > 5 else 0.0
            ) for row in raw
        ]
        return {
            "exchange": req.exchange,
            "symbol": req.symbol,
            "timeframe": req.timeframe,
            "data": data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream exchange error")
