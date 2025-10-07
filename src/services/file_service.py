import json
import os
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete

from src.models import Product, ProductOffer, ProductAttribute, ProductImage, ProductPriceHistory, ProductOfferHistory
from src.core.dependencies import SessionLocal

from logs.config_logs import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


def save_scraped_data(scraped_data: Dict[str, Any], product_id: str) -> None:
    current_time = scraped_data.get("fetched_at", datetime.utcnow().isoformat() + "Z")
    offers_count = scraped_data.get("offers_amount", len(scraped_data.get("offers", [])))
    
    # Сохраняем данные в JSON файлы
    save_product_data(scraped_data, product_id, current_time, offers_count)
    save_offers_data(scraped_data, product_id, current_time, offers_count)
    
    # Сохраняем данные в базу данных (синхронно)
    save_to_database(scraped_data, product_id)


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


def save_to_database(scraped_data: Dict[str, Any], product_id: str) -> None:
    """
    Сохраняет данные продукта в базу данных (синхронно).
    
    Args:
        scraped_data: Полные данные продукта
        product_id: ID продукта из Kaspi
    """
    try:
        with SessionLocal() as session:
            # Проверяем, существует ли уже продукт
            stmt = select(Product).filter_by(kaspi_id=product_id)
            result = session.execute(stmt)
            existing_product = result.scalar_one_or_none()
            
            if existing_product:
                # Обновляем существующий продукт
                product = existing_product
                _update_product_from_data(product, scraped_data)
                logger.info(f"Обновляем продукт с kaspi_id: {product_id}")
                # Принудительно помечаем объект как измененный
                session.add(product)
            else:
                # Создаем новый продукт
                product = _create_product_from_data(scraped_data, product_id)
                session.add(product)
                logger.info(f"Создаем новый продукт с kaspi_id: {product_id}")
            
            # Flush чтобы SQLAlchemy понял что объект изменился
            session.flush()
            
            # Коммитим изменения продукта, чтобы получить product.id
            session.commit()
            session.refresh(product)
            
            # Сохраняем связанные данные
            _save_product_images(session, product.id, scraped_data.get("images", []))
            _save_product_attributes(session, product.id, scraped_data.get("attributes", {}))
            _save_product_offers(session, product.id, scraped_data.get("offers", []))
            _save_product_price_history(session, product.id, scraped_data)
            
            # Финальный коммит
            session.commit()
            logger.info(f"Продукт {product_id} успешно сохранен в БД")
            
    except IntegrityError as e:
        logger.error(f"Ошибка целостности данных при сохранении продукта {product_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении продукта {product_id} в БД: {e}")


def _create_product_from_data(scraped_data: Dict[str, Any], product_id: str) -> Product:
    """Создает новый объект Product из данных."""
    now = datetime.utcnow()
    return Product(
        kaspi_id=product_id,
        url=scraped_data.get("url", ""),
        name=scraped_data.get("name", ""),
        category=scraped_data.get("category"),
        price_min=scraped_data.get("price_min"),
        price_max=scraped_data.get("price_max"),
        rating=scraped_data.get("rating"),
        reviews_count=scraped_data.get("reviews_count", 0),
        offers_count=scraped_data.get("offers_amount", 0),
        # Явно устанавливаем created_at и updated_at для новых продуктов
        created_at=now,
        updated_at=now
    )


def _update_product_from_data(product: Product, scraped_data: Dict[str, Any]) -> None:
    """Обновляет существующий продукт данными из scraped_data."""
    product.name = scraped_data.get("name", product.name)
    product.category = scraped_data.get("category", product.category)
    product.price_min = scraped_data.get("price_min")
    product.price_max = scraped_data.get("price_max")
    product.rating = scraped_data.get("rating")
    product.reviews_count = scraped_data.get("reviews_count", product.reviews_count)
    product.offers_count = scraped_data.get("offers_amount", 0)
    # Явно обновляем updated_at
    product.updated_at = datetime.utcnow()


def _save_product_images(session, product_id: int, images: list) -> None:
    """Сохраняет изображения продукта."""
    # Удаляем старые изображения через DELETE запрос
    delete_stmt = delete(ProductImage).filter_by(product_id=product_id)
    session.execute(delete_stmt)
    
    # Добавляем новые
    for image_url in images:
        if image_url:  # Проверяем, что URL не пустой
            image = ProductImage(
                product_id=product_id,
                image_url=image_url
            )
            session.add(image)


def _save_product_attributes(session, product_id: int, attributes: dict) -> None:
    """Сохраняет атрибуты продукта."""
    # Удаляем старые атрибуты через DELETE запрос
    delete_stmt = delete(ProductAttribute).filter_by(product_id=product_id)
    session.execute(delete_stmt)
    
    # Добавляем новые атрибуты
    def _add_attributes_recursive(attrs, prefix=""):
        for key, value in attrs.items():
            if isinstance(value, dict):
                # Если значение - словарь, добавляем атрибуты рекурсивно
                new_prefix = f"{prefix}{key}." if prefix else f"{key}."
                _add_attributes_recursive(value, new_prefix)
            else:
                # Обычный атрибут
                full_key = f"{prefix}{key}" if prefix else key
                attribute = ProductAttribute(
                    product_id=product_id,
                    attribute_name=full_key,
                    attribute_value=str(value) if value is not None else ""
                )
                session.add(attribute)
    
    _add_attributes_recursive(attributes)


def _save_product_offers(session, product_id: int, offers: list) -> None:
    """Сохраняет предложения продукта и историю изменений цен."""
    # Получаем существующие предложения
    stmt = select(ProductOffer).filter_by(product_id=product_id)
    result = session.execute(stmt)
    existing_offers = {offer.seller_name: offer for offer in result.scalars().all()}
    
    # Обрабатываем новые предложения
    for offer_data in offers:
        if isinstance(offer_data, dict):
            seller_name = offer_data.get("merchant_name", "Unknown")
            new_price = offer_data.get("price")
            
            if seller_name in existing_offers:
                # Предложение существует - проверяем изменение цены
                existing_offer = existing_offers[seller_name]
                if existing_offer.price != new_price and new_price is not None:
                    # Цена изменилась - сохраняем в историю
                    history = ProductOfferHistory(
                        offer_id=existing_offer.id,
                        old_price=existing_offer.price,
                        new_price=new_price
                    )
                    session.add(history)
                    # Обновляем цену предложения
                    existing_offer.price = new_price
                
                # Обновляем last_seen (затрагиваем все поля ProductOffer)
                existing_offer.last_seen = datetime.utcnow()
                # Удаляем из словаря обработанных
                del existing_offers[seller_name]
            else:
                # Новое предложение
                offer = ProductOffer(
                    product_id=product_id,
                    seller_name=seller_name,
                    price=new_price
                )
                session.add(offer)
    
    # Удаляем предложения, которых больше нет в данных
    for remaining_offer in existing_offers.values():
        session.delete(remaining_offer)


def _save_product_price_history(session, product_id: int, scraped_data: Dict[str, Any]) -> None:
    """Сохраняет историю цен продукта."""
    price_min = scraped_data.get("price_min")
    price_max = scraped_data.get("price_max")
    
    if price_min is not None or price_max is not None:
        price_history = ProductPriceHistory(
            product_id=product_id,
            price_min=price_min,
            price_max=price_max
        )
        session.add(price_history)