import json
import os
from datetime import datetime
from typing import Dict, Any


def save_scraped_data(scraped_data: Dict[str, Any], product_id: str) -> None:
    current_time = scraped_data.get("fetched_at", datetime.utcnow().isoformat() + "Z")
    offers_count = scraped_data.get("offers_amount", len(scraped_data.get("offers", [])))
    
    save_product_data(scraped_data, product_id, current_time, offers_count)
    
    save_offers_data(scraped_data, product_id, current_time, offers_count)


def save_product_data(scraped_data: Dict[str, Any], product_id: str, 
                     fetched_at: str, offers_amount: int) -> None:
    product_data = {k: v for k, v in scraped_data.items() if k != "offers"}
    product_data["fetched_at"] = fetched_at
    product_data["offers_amount"] = offers_amount
    
    products_dir = "export/products"
    os.makedirs(products_dir, exist_ok=True)
    
    product_filename = f"product_{product_id}.json"
    product_filepath = os.path.join(products_dir, product_filename)
    
    with open(product_filepath, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)


def save_offers_data(scraped_data: Dict[str, Any], product_id: str,
                    fetched_at: str, offers_amount: int) -> None:
    offers_data = {
        "fetched_at": fetched_at,
        "offers_amount": offers_amount,
        "offers": scraped_data.get("offers", [])
    }
    
    offers_dir = "export/offers"
    os.makedirs(offers_dir, exist_ok=True)
    
    offers_filename = f"offers_{product_id}.json"
    offers_filepath = os.path.join(offers_dir, offers_filename)
    
    with open(offers_filepath, 'w', encoding='utf-8') as f:
        json.dump(offers_data, f, ensure_ascii=False, indent=2)