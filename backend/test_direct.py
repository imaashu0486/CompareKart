"""Direct uvicorn server without subprocess."""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from database import init_db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle."""
    try:
        logger.info("Starting app...")
        init_db()
        logger.info("Database initialized")
        yield
    except Exception as e:
        logger.error(f"Error in startup: {e}", exc_info=True)
        raise
    finally:
        try:
            logger.info("Shutting down app...")
        except Exception as e:
            logger.error(f"Error in shutdown: {e}", exc_info=True)


# Create app
app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check."""
    logger.info("Health endpoint called")
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root."""
    logger.info("Root endpoint called")
    return {"message": "Hello"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server...")
    # Create config
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="debug",
        access_log=True,
        use_colors=False,
    )
    server = uvicorn.Server(config)
    
    import asyncio
    asyncio.run(server.serve())
