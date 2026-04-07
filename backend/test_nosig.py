"""Direct uvicorn server with signal handling disabled."""
import logging
import sys
import signal
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from database import init_db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle."""
    logger.info("Starting app...")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down app...")


# Create app
app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root."""
    return {"message": "Hello"}


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Disable signal handlers on Windows
    if sys.platform == "win32":
        # This prevents SIGTERM from being sent
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
    
    logger.info("Starting uvicorn server (signal handling disabled)...")
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True,
    )
    server = uvicorn.Server(config)
    
    import asyncio
    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
