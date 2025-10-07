from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum



class ProductBase(BaseModel):
    """Base product model."""
    url: str
    name: str
    category: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    sellers_count: Optional[int] = None


class ProductUpdate(BaseModel):
    """Product update model."""
    name: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    sellers_count: Optional[int] = None


class ProductPrice(BaseModel):
    """Product price model."""
    id: int
    product_id: int
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    fetched_at: datetime

    class Config:
        from_attributes = True


class ProductOffer(BaseModel):
    """Product offer model."""
    id: int
    product_id: int
    seller_name: Optional[str] = None
    price: Optional[float] = None
    last_seen: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class ProductAttribute(BaseModel):
    """Product attribute model."""
    id: int
    product_id: int
    attribute_name: Optional[str] = None
    attribute_value: Optional[str] = None

    class Config:
        from_attributes = True


class ProductImage(BaseModel):
    """Product image model."""
    id: int
    product_id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class Product(ProductBase):
    """Full product model with relations."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    prices: List[ProductPrice] = []
    offers: List[ProductOffer] = []
    attributes: List[ProductAttribute] = []
    images: List[ProductImage] = []

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Product response for API."""
    id: int
    url: str
    name: str
    category: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    sellers_count: Optional[int] = None
    current_price_min: Optional[float] = None
    current_price_max: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductExport(BaseModel):
    """Product export model for JSON."""
    url: str
    name: str
    category: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    sellers_count: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    images: List[str] = []
    attributes: dict = {}
    scraped_at: datetime


class OfferExport(BaseModel):
    """Offer export model for JSONL."""
    seller_name: str
    price: float
    product_url: str
    scraped_at: datetime


class ParseStatus(BaseModel):
    """Parse status response."""
    status: str
    message: str
    product_url: Optional[str] = None
    scraped_at: Optional[datetime] = None


# API Request/Response models
class SeedRequest(BaseModel):
    """Seed product URL request."""
    product_url: str


class SeedResponse(BaseModel):
    """Seed response."""
    product_id: int
    url: str
    message: str


class ScrapeRequest(BaseModel):
    """Scrape request."""
    product_url: str


class ScrapeResponse(BaseModel):
    """Scrape response."""
    task: str
    url: str
    product_id: Optional[int] = None
    task_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    uptime: int
    version: str = "1.0.0"


class ProductList(BaseModel):
    """Product list response."""
    id: int
    name: str
    url: str
    current_price_min: Optional[float] = None
    current_price_max: Optional[float] = None
    rating: Optional[float] = None
    last_updated: Optional[datetime] = None


class ProductOut(BaseModel):
    """Full product output."""
    id: int
    name: str
    url: str
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    sellers_count: Optional[int] = None
    images: List[str] = []
    attributes: dict = {}
    last_updated: Optional[datetime] = None