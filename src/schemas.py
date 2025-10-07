from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# API Request/Response models
class SeedRequest(BaseModel):
    """Seed product URL request."""
    product_url: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    uptime: int
    version: str = "1.0.0"
