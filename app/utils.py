from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI

def register_error_handlers(app: FastAPI):
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
