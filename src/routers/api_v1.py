from fastapi import APIRouter, Depends, HTTPException

router = APIRouter("/parser", tags=["parser"])

@router.post("/seed")
def seed_data():
    pass

@router.post("/scrape")
def scrape_data():
    pass

