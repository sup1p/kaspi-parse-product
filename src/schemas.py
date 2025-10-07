from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

# API Request/Response models
class SeedRequest(BaseModel):
    """Seed product URL request."""
    product_url: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    uptime: int
    version: str = "1.0.0"


# Product schemas
class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    image_url: str
    created_at: datetime


class ProductAttributeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    attribute_name: str
    attribute_value: str


class ProductOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    seller_name: str
    price: Optional[float]
    last_seen: datetime


class ProductOfferHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    offer_id: int
    old_price: Optional[float]
    new_price: Optional[float]
    changed_at: datetime
    offer: Optional[ProductOfferResponse] = None


class ProductPriceHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    price_min: Optional[float]
    price_max: Optional[float]
    recorded_at: datetime


class ProductBaseResponse(BaseModel):
    """Базовая схема продукта без связанных данных (для списков)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    kaspi_id: str
    url: str
    name: str
    category: Optional[str]
    price_min: Optional[float]
    price_max: Optional[float]
    rating: Optional[float]
    reviews_count: Optional[int]
    offers_count: int
    created_at: datetime
    updated_at: Optional[datetime]


class ProductResponse(ProductBaseResponse):
    """Полная схема продукта со связанными данными."""
    
    # Связанные данные (опционально)
    images: List[ProductImageResponse] = []
    attributes: List[ProductAttributeResponse] = []
    offers: List[ProductOfferResponse] = []
    prices: List[ProductPriceHistoryResponse] = []


class ProductListResponse(BaseModel):
    """Ответ для списка продуктов с пагинацией."""
    products: List[ProductBaseResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ProductDetailedListResponse(BaseModel):
    """Ответ для списка продуктов с полными данными."""
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ProductStatsResponse(BaseModel):
    """Статистика по продукту."""
    product_id: int
    total_offers: int
    cheapest_price: Optional[float]
    most_expensive_price: Optional[float]
    price_range: Optional[float]
    avg_price: Optional[float]


# Export schemas for JSON files
class ExportProductResponse(BaseModel):
    """Схема для экспорта продукта из JSON файлов."""
    url: str
    name: str
    category: Optional[str]
    price_min: Optional[float]
    price_max: Optional[float]
    rating: Optional[float]
    reviews_count: Optional[int]
    images: List[str]
    attributes: Dict[str, Any]
    fetched_at: str
    offers_amount: int


class ExportOffersResponse(BaseModel):
    """Схема для экспорта предложений из JSON файлов."""
    fetched_at: str
    offers_amount: int
    offers: List[Dict[str, Any]]
