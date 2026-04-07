"""Test script to check startup issues."""
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

try:
    logger.info("Attempting to import main...")
    from main import app
    logger.info("Successfully imported app from main")
    
    logger.info("Attempting to create test client...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    logger.info("Test client created successfully")
    
    logger.info("Testing health endpoint...")
    response = client.get("/health")
    logger.info(f"Health endpoint response: {response.status_code} - {response.json()}")
    
except Exception as e:
    logger.error(f"Error during startup test: {str(e)}", exc_info=True)
    sys.exit(1)
