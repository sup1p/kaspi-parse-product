from sys import prefix
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
def get_products():
    pass

@router.get("/{product_id}")
def get_product(product_id: int):
    pass

@router.get("/{product_id}/prices")
def get_product_prices(product_id: int):
    pass

@router.get("/{product_id}/offers")
def get_product_offers(product_id: int):
    pass

@router.get("/{product_id}/offers/history")
def get_product_offers_history(product_id: int):
    pass

@router.get("/export/{product_id}")
def export_product_data(product_id: int):
    pass

@router.get("/export/{product_id}/offers")
def export_product_offers(product_id: int):
    pass