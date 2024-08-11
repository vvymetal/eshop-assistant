from fastapi import APIRouter, Depends
from app.services.product_service import ProductService

router = APIRouter()

@router.get("/products")
async def get_products(product_service: ProductService = Depends(ProductService)):
    return product_service.get_all_products()

@router.get("/products/{product_id}")
async def get_product(product_id: int, product_service: ProductService = Depends(ProductService)):
    product = product_service.get_product(product_id)
    if product:
        return product
    return {"error": "Product not found"}