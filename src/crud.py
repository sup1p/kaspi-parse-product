from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, desc, func

from src.models import Product, ProductOffer, ProductAttribute, ProductImage, ProductPriceHistory, ProductOfferHistory


# Product CRUD operations
def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """Получить продукт по ID с загрузкой связанных данных."""
    stmt = (
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.offers),
            selectinload(Product.prices)
        )
        .where(Product.id == product_id)
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def get_product_by_kaspi_id(db: Session, kaspi_id: str) -> Optional[Product]:
    """Получить продукт по Kaspi ID с загрузкой связанных данных."""
    stmt = (
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.offers),
            selectinload(Product.prices)
        )
        .where(Product.kaspi_id == kaspi_id)
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None
) -> List[Product]:
    """Получить список продуктов с пагинацией и фильтрацией (без связанных данных)."""
    stmt = select(Product).offset(skip).limit(limit)
    
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
    
    stmt = stmt.order_by(desc(Product.created_at))
    result = db.execute(stmt)
    return result.scalars().all()


def get_products_with_relations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None
) -> List[Product]:
    """Получить список продуктов с полными связанными данными."""
    stmt = (
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.offers),
            selectinload(Product.prices)
        )
        .offset(skip)
        .limit(limit)
    )
    
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
    
    stmt = stmt.order_by(desc(Product.created_at))
    result = db.execute(stmt)
    return result.scalars().all()


# Product Offers CRUD operations
def get_product_offers(db: Session, product_id: int) -> List[ProductOffer]:
    """Получить все предложения для продукта."""
    stmt = (
        select(ProductOffer)
        .where(ProductOffer.product_id == product_id)
        .order_by(ProductOffer.price)
    )
    result = db.execute(stmt)
    return result.scalars().all()


def get_product_offers_history(
    db: Session, 
    product_id: int,
    limit: int = 100
) -> List[ProductOfferHistory]:
    """Получить историю изменения предложений для продукта."""
    # Сначала получаем все offer_id для данного продукта
    offers_stmt = select(ProductOffer.id).where(ProductOffer.product_id == product_id)
    offers_result = db.execute(offers_stmt)
    offer_ids = [row[0] for row in offers_result.fetchall()]
    
    if not offer_ids:
        return []
    
    # Затем получаем историю для этих предложений
    stmt = (
        select(ProductOfferHistory)
        .options(selectinload(ProductOfferHistory.offer))
        .where(ProductOfferHistory.offer_id.in_(offer_ids))
        .order_by(desc(ProductOfferHistory.changed_at))
        .limit(limit)
    )
    result = db.execute(stmt)
    return result.scalars().all()


# Product Price History CRUD operations
def get_product_price_history(
    db: Session, 
    product_id: int,
    limit: int = 100
) -> List[ProductPriceHistory]:
    """Получить историю изменения цен продукта."""
    stmt = (
        select(ProductPriceHistory)
        .where(ProductPriceHistory.product_id == product_id)
        .order_by(desc(ProductPriceHistory.recorded_at))
        .limit(limit)
    )
    result = db.execute(stmt)
    return result.scalars().all()


# Product Attributes CRUD operations
def get_product_attributes(db: Session, product_id: int) -> List[ProductAttribute]:
    """Получить все атрибуты продукта."""
    stmt = (
        select(ProductAttribute)
        .where(ProductAttribute.product_id == product_id)
        .order_by(ProductAttribute.attribute_name)
    )
    result = db.execute(stmt)
    return result.scalars().all()


# Product Images CRUD operations
def get_product_images(db: Session, product_id: int) -> List[ProductImage]:
    """Получить все изображения продукта."""
    stmt = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.created_at)
    )
    result = db.execute(stmt)
    return result.scalars().all()


# Statistics and aggregation functions
def get_products_count(db: Session, category: Optional[str] = None) -> int:
    """Получить количество продуктов."""
    stmt = select(func.count(Product.id))
    
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
    
    result = db.execute(stmt)
    return result.scalar() or 0


def get_cheapest_offer_for_product(db: Session, product_id: int) -> Optional[ProductOffer]:
    """Получить самое дешевое предложение для продукта."""
    stmt = (
        select(ProductOffer)
        .where(ProductOffer.product_id == product_id)
        .where(ProductOffer.price.isnot(None))
        .order_by(ProductOffer.price)
        .limit(1)
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def get_most_expensive_offer_for_product(db: Session, product_id: int) -> Optional[ProductOffer]:
    """Получить самое дорогое предложение для продукта."""
    stmt = (
        select(ProductOffer)
        .where(ProductOffer.product_id == product_id)
        .where(ProductOffer.price.isnot(None))
        .order_by(desc(ProductOffer.price))
        .limit(1)
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()
