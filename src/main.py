import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import health, api_v1, products
from logs.config_logs import setup_logging

setup_logging()



app = FastAPI()
logger = logging.getLogger(__name__)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(api_v1.router)
app.include_router(products.router)


@app.get("/")
def root():
    """Root endpoint - redirects to health check."""
    logger.info("Root endpoint accessed")
    return {"message": "TZVR API is running", "docs": "/docs", "health": "/health"}