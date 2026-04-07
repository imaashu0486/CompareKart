"""Minimal test FastAPI app."""
import logging
import sys
import traceback
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

# Set uvicorn logger level
logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)


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


@app.middleware("http")
async def error_middleware(request: Request, call_next):
    """Catch any errors in middleware chain."""
    try:
        logger.debug(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Middleware error: {e}", exc_info=True)
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/health")
async def health():
    """Health check."""
    try:
        logger.debug("Health check called")
        result = {"status": "healthy"}
        logger.debug(f"Returning: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in health: {e}", exc_info=True)
        raise


@app.get("/")
async def root():
    """Root."""
    try:
        logger.debug("Root called")
        return {"message": "Hello"}
    except Exception as e:
        logger.error(f"Error in root: {e}", exc_info=True)
        raise


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Catch all exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn...")
    uvicorn.run(
        "test_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="debug",
    )

