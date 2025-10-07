from fastapi import APIRouter, HTTPException

from src.services.kaspi_parser import parse_kaspi_product_with_bs
from src.services.file_service import save_scraped_data
from src.utils import is_valid_kaspi_url, extract_product_id_from_url
from src.schemas import SeedRequest


router = APIRouter(prefix="/parser", tags=["parser"])

@router.post("/scrape-props")
def scrape_props(data: SeedRequest):
    url = data.product_url
    
    if not is_valid_kaspi_url(url):
        raise HTTPException(status_code=400, detail="Invalid Kaspi URL")
    try:
        product_id = extract_product_id_from_url(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot extract product ID from URL / Internet problems: {e}")
    
    scraped_data = parse_kaspi_product_with_bs(url, headless=True)
    
    # Сохраняем данные в файлы через сервис
    save_scraped_data(scraped_data, product_id)
    
    return scraped_data