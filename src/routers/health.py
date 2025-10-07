import time
from fastapi import APIRouter
from src.schemas import HealthResponse

router = APIRouter(tags=["health"])

# App start time for uptime calculation
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = int(time.time() - start_time)
    return HealthResponse(
        status="ok",
        uptime=uptime,
        version="1.0.0"
    )