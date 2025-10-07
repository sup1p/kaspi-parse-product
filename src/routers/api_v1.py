from fastapi import APIRouter, Depends, HTTPException
from src.services.kaspi_parser import fetch_offers, get_category_path, parse_kaspi_product_with_bs

router = APIRouter(prefix="/parser", tags=["parser"])

@router.post("/scrape-offers")
def scrape_offers():
    url = "https://kaspi.kz/shop/p/apple-iphone-16-pro-max-256gb-zolotistyi-123890547/?c=750000000"
    return fetch_offers(url)