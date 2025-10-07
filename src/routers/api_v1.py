from fastapi import APIRouter, HTTPException

from src.services.kaspi_parser import parse_kaspi_product_with_bs
from src.utils import is_valid_kaspi_url
from src.schemas import SeedRequest


router = APIRouter(prefix="/parser", tags=["parser"])

@router.post("/scrape-props")
def scrape_props(data: SeedRequest):
    url = data.product_url
    if not is_valid_kaspi_url(url):
        raise HTTPException(status_code=400, detail="Invalid Kaspi URL")
    
    data = parse_kaspi_product_with_bs(url, headless=True)
    return data