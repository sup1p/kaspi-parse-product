import time
from fastapi import APIRouter
from src.schemas import HealthResponse
from logs.config_logs import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)



router = APIRouter(tags=["health"])

# App start time for uptime calculation
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = int(time.time() - start_time)
    logger.info("Health check endpoint accessed")
    return HealthResponse(
        status="ok",
        uptime=uptime,
        version="1.0.0"
    )