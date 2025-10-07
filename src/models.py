from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    kaspi_id = Column(String, unique=True, nullable=False)
    url = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    category = Column(Text)
    price_min = Column(Float)
    price_max = Column(Float)
    rating = Column(Float)
    offers_count = Column(Integer)
    reviews_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prices = relationship("ProductPriceHistory", back_populates="product")
    offers = relationship("ProductOffer", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    attributes = relationship("ProductAttribute", back_populates="product")

class ProductOffer(Base):
    __tablename__ = "product_offers"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    seller_name = Column(String)
    price = Column(Float)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
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

class ProductAttribute(Base):
    __tablename__ = "product_attributes"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    attribute_name = Column(String)
    attribute_value = Column(Text)
    product = relationship("Product", back_populates="attributes")

class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    product = relationship("Product", back_populates="images")

class ProductPriceHistory(Base):
    __tablename__ = "product_price_history"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    price_min = Column(Float)
    price_max = Column(Float)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    product = relationship("Product", back_populates="prices")
