from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/parser", tags=["parser"])

@router.post("/seed")
def seed_data():
    pass

@router.post("/scrape")
def scrape_data():
    pass

