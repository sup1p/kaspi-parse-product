from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    category = Column(Text)
    rating = Column(Float)
    reviews_count = Column(Integer)
    sellers_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    prices = relationship("ProductPriceHistory", back_populates="product")
    offers = relationship("ProductOffer", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    attributes = relationship("ProductAttribute", back_populates="product")

class ProductPriceHistory(Base):
    __tablename__ = "product_prices_history"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    price_min = Column(Float)
    price_max = Column(Float)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    product = relationship("Product", back_populates="prices")

class ProductOffer(Base):
    __tablename__ = "product_offers"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    seller_name = Column(String)
    price = Column(Float)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    product = relationship("Product", back_populates="offers")
    history = relationship("ProductOfferHistory", back_populates="offer")

class ProductOfferHistory(Base):
    __tablename__ = "product_offers_history"
    id = Column(Integer, primary_key=True)
    offer_id = Column(Integer, ForeignKey("product_offers.id", ondelete="CASCADE"))
    old_price = Column(Float)
    new_price = Column(Float)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    offer = relationship("ProductOffer", back_populates="history")

class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(Text)
    product = relationship("Product", back_populates="images")

class ProductAttribute(Base):
    __tablename__ = "product_attributes"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    attribute_name = Column(String)
    attribute_value = Column(Text)
    product = relationship("Product", back_populates="attributes")
