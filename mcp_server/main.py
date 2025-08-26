import logging
from fastapi import FastAPI
from .handlers import router
from .streaming import router as streaming_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

app = FastAPI(
    title="MCP Server Example",
    description="MCP Server with WebSocket streaming and LangGraph agents",
    version="1.0.0"
)

# Add CORS middleware for WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    logger.info("MCP Server is starting up...")

# Mount the handlers router
logger.info("Mounting handlers router.")
app.include_router(router)

# Mount the streaming router
logger.info("Mounting streaming router.")
app.include_router(streaming_router, prefix="/api/v1", tags=["streaming"])

# --- Serve static UI files from 'ui/build' directory at root path ---
UI_BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui", "build"))
if os.path.isdir(UI_BUILD_DIR):
    logger.info(f"Serving static UI from {UI_BUILD_DIR} at root path.")
    app.mount("/", StaticFiles(directory=UI_BUILD_DIR, html=True), name="ui")
else:
    logger.warning(f"UI build directory not found: {UI_BUILD_DIR}. UI will not be served.")

# Import handlers to register endpoints
from . import handlers  # noqa 