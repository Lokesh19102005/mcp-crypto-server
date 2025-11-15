"""app package for MCP Crypto Server"""

__version__ = "0.1.0"

# make the FastAPI app importable as `from app import app`
try:
    from .main import app  # created in main.py
except Exception:  # avoid import error during tests/setup until main.py exists
    app = None

# expose useful names for external imports
from .routes import router as api_router  # noqa: E402,F401

__all__ = ["app", "api_router", "__version__"]
