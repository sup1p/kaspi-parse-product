import json
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from math import ceil
import logging

from src.core.dependencies import get_session
from src import crud
from src.schemas import (
    ProductResponse, 
    ProductBaseResponse,
    ProductListResponse,
    ProductDetailedListResponse,
    ProductOfferResponse,
    ProductOfferHistoryResponse,
    ProductPriceHistoryResponse,
    ExportProductResponse,
    ExportOffersResponse,
    ProductStatsResponse
)

from logs.config_logs import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductListResponse)
def get_products(
    skip: int = Query(0, ge=0, description="Количество продуктов для пропуска"),
    limit: int = Query(20, ge=1, le=100, description="Количество продуктов на странице"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    db: Session = Depends(get_session)
):
    """Получить список продуктов с пагинацией и фильтрацией."""
    
    logger.info(f"Getting products list: skip={skip}, limit={limit}, category={category}")
    
    # Получаем продукты
    products = crud.get_products(db, skip=skip, limit=limit, category=category)
    
    # Получаем общее количество
    total = crud.get_products_count(db, category=category)
    
    # Рассчитываем пагинацию
    page = (skip // limit) + 1
    total_pages = ceil(total / limit) if total > 0 else 1
    
    return ProductListResponse(
        products=products,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )


@router.get("/detailed", response_model=ProductDetailedListResponse)
def get_products_detailed(
    skip: int = Query(0, ge=0, description="Количество продуктов для пропуска"),
    limit: int = Query(10, ge=1, le=50, description="Количество продуктов на странице"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    db: Session = Depends(get_session)
):
    """Получить список продуктов со всеми связанными данными."""
    
    # Получаем продукты с полными данными
    products = crud.get_products_with_relations(db, skip=skip, limit=limit, category=category)
    
    # Получаем общее количество
    total = crud.get_products_count(db, category=category)
    
    # Рассчитываем пагинацию
    page = (skip // limit) + 1
    total_pages = ceil(total / limit) if total > 0 else 1
    
    return ProductDetailedListResponse(
        products=products,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_session)
):
    """Получить продукт по ID со всеми связанными данными."""
    
    logger.info(f"Getting product by ID: {product_id}")
    
    product = crud.get_product_by_id(db, product_id)
    if not product:
        logger.warning(f"Product not found: {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    logger.info(f"Successfully retrieved product: {product_id}")
    return product


@router.get("/{product_id}/prices", response_model=list[ProductPriceHistoryResponse])
def get_product_prices(
    product_id: int,
    limit: int = Query(50, ge=1, le=200, description="Количество записей истории"),
    db: Session = Depends(get_session)
):
    """Получить историю цен продукта."""
    
    # Проверяем, что продукт существует
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    price_history = crud.get_product_price_history(db, product_id, limit=limit)
    return price_history


@router.get("/{product_id}/offers", response_model=list[ProductOfferResponse])
def get_product_offers(
    product_id: int,
    db: Session = Depends(get_session)
):
    """Получить все предложения для продукта."""
    
    # Проверяем, что продукт существует
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    offers = crud.get_product_offers(db, product_id)
    return offers


@router.get("/{product_id}/offers/history", response_model=list[ProductOfferHistoryResponse])
def get_product_offers_history(
    product_id: int,
    limit: int = Query(100, ge=1, le=500, description="Количество записей истории"),
    db: Session = Depends(get_session)
):
    """Получить историю изменения предложений продукта."""
    
    # Проверяем, что продукт существует
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    offers_history = crud.get_product_offers_history(db, product_id, limit=limit)
    return offers_history


@router.get("/{product_id}/stats", response_model=ProductStatsResponse)
def get_product_stats(
    product_id: int,
    db: Session = Depends(get_session)
):
    """Получить статистику по продукту."""
    
    # Проверяем, что продукт существует
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Получаем предложения
    offers = crud.get_product_offers(db, product_id)
    
    # Получаем самые дешевые и дорогие предложения
    cheapest = crud.get_cheapest_offer_for_product(db, product_id)
    most_expensive = crud.get_most_expensive_offer_for_product(db, product_id)
    
    # Рассчитываем статистику
    prices = [offer.price for offer in offers if offer.price is not None]
    avg_price = sum(prices) / len(prices) if prices else None
    
    cheapest_price = cheapest.price if cheapest else None
    most_expensive_price = most_expensive.price if most_expensive else None
    price_range = (most_expensive_price - cheapest_price) if (cheapest_price and most_expensive_price) else None
    
    return ProductStatsResponse(
        product_id=product_id,
        total_offers=len(offers),
        cheapest_price=cheapest_price,
        most_expensive_price=most_expensive_price,
        price_range=price_range,
        avg_price=avg_price
    )


@router.get("/kaspi/{kaspi_id}", response_model=ProductResponse)
def get_product_by_kaspi_id(
    kaspi_id: str,
    db: Session = Depends(get_session)
):
    """Получить продукт по Kaspi ID."""
    
    product = crud.get_product_by_kaspi_id(db, kaspi_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


# Export endpoints (работают с JSON файлами)
@router.get("/export/{kaspi_id}", response_model=ExportProductResponse)
def export_product_data(kaspi_id: str):
    """Экспорт данных продукта из JSON файла."""
    
    logger.info(f"Exporting product data for kaspi_id: {kaspi_id}")
    
    product_file = f"export/products/product_{kaspi_id}.json"

    if not os.path.exists(product_file):
        logger.warning(f"Product export file not found: {product_file}")
        raise HTTPException(status_code=404, detail="Product export file not found")
    
    try:
        with open(product_file, 'r', encoding='utf-8') as f:
            product_data = json.load(f)
        logger.info(f"Successfully exported product data for kaspi_id: {kaspi_id}")
        return product_data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file for kaspi_id {kaspi_id}: {e}")
        raise HTTPException(status_code=500, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.get("/export/{kaspi_id}/offers", response_model=ExportOffersResponse)
def export_product_offers(kaspi_id: str):
    """Экспорт предложений продукта из JSON файла."""
    
    logger.info(f"Exporting product offers for kaspi_id: {kaspi_id}")
    
    offers_file = f"export/offers/offers_{kaspi_id}.json"
    if not os.path.exists(offers_file):
        logger.warning(f"Product offers export file not found: {offers_file}")
        raise HTTPException(status_code=404, detail="Product offers export file not found")
    
    try:
        with open(offers_file, 'r', encoding='utf-8') as f:
            offers_data = json.load(f)
        logger.info(f"Successfully exported offers for kaspi_id: {kaspi_id}")
        return offers_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
