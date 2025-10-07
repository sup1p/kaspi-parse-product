import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import health, api_v1, products

app = FastAPI()

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
    return {"message": "TZVR API is running", "docs": "/docs", "health": "/health"}