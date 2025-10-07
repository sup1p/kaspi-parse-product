import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.dependencies import get_db
from ..schemas import HealthResponse

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