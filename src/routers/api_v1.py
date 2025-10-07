from fastapi import APIRouter, HTTPException

from src.services.kaspi_parser import parse_kaspi_product_with_bs
from src.services.file_service import save_scraped_data
from src.utils import is_valid_kaspi_url, extract_product_id_from_url
from src.schemas import SeedRequest

from logs.config_logs import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/parser", tags=["parser"])

@router.post("/scrape-props")
def scrape_props(data: SeedRequest):
    logger.info(f"Starting scrape for URL: {data.product_url}")
    
    url = data.product_url
    
    if not is_valid_kaspi_url(url):
        logger.warning(f"Invalid Kaspi URL provided: {url}")
        raise HTTPException(status_code=400, detail="Invalid Kaspi URL")
    try:
        product_id = extract_product_id_from_url(url)
        logger.info(f"Extracted product ID: {product_id}")
    except Exception as e:
        logger.error(f"Failed to extract product ID from URL {url}: {e}")
        raise HTTPException(status_code=400, detail=f"Cannot extract product ID from URL / Internet problems: {e}")
    
    logger.info(f"Starting parsing for product {product_id}")
    scraped_data = parse_kaspi_product_with_bs(url, headless=True)
    
    # Сохраняем данные в файлы через сервис
    logger.info(f"Saving scraped data for product {product_id}")
    save_scraped_data(scraped_data, product_id)
    
    logger.info(f"Successfully completed scraping for product {product_id}")
    return scraped_data