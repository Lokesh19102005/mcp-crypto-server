from fastapi import FastAPI, WebSocket
import uvicorn
from .routes import router as api_router
from .ws import manager
from .exchanges import ExchangeClient
from .utils import register_error_handlers

app = FastAPI(title="MCP Crypto Server")
# register local/custom error handlers (e.g. ValueError -> 400)
register_error_handlers(app)
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup():
    # Create exchange client instance (shared)
    app.state.exchange = ExchangeClient()
    await app.state.exchange.startup()
    # Optionally start background tasks (e.g., broadcaster) -- left simple for this assignment

@app.on_event("shutdown")
async def shutdown():
    await app.state.exchange.shutdown()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()  # simple echo/subscribe messages expected as JSON in production
            # in a fuller implementation parse subscribe/unsubscribe for symbols
            await ws.send_text(f"received: {data}")
    except Exception:
        pass
    finally:
        await manager.disconnect(ws)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
