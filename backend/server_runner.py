"""Server runner with PID file."""
import logging
import sys
import os
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
    
    # Write PID file
    pid = os.getpid()
    with open("server.pid", "w") as f:
        f.write(str(pid))
    logger.info(f"Server PID: {pid}")
    
    yield
    
    logger.info("Shutting down app...")
    # Clean up PID file
    try:
        os.remove("server.pid")
    except:
        pass


# Create app
app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check."""
    logger.info("Health endpoint hit")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )

