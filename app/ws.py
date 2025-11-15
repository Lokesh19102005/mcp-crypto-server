from fastapi import WebSocket
from typing import List
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active:
                self.active.remove(websocket)

    async def broadcast(self, message: str):
        async with self._lock:
            for conn in list(self.active):
                try:
                    await conn.send_text(message)
                except Exception:
                    pass

manager = ConnectionManager()
