from fastapi import APIRouter, Depends
from backend.app.services.cart_service import CartService

router = APIRouter()

@router.get("/")
async def get_cart(cart_service: CartService = Depends(CartService)):
    return cart_service.get_cart()

@router.post("/add")
async def add_to_cart(item_id: int, quantity: int = 1, cart_service: CartService = Depends(CartService)):
    return cart_service.add_item(item_id, quantity)

@router.delete("/remove/{item_id}")
async def remove_from_cart(item_id: int, cart_service: CartService = Depends(CartService)):
    return cart_service.remove_item(item_id)

# backend/app/api/products.py

from fastapi import APIRouter, Depends
from backend.app.services.product_service import ProductService

router = APIRouter()

@router.get("/")
async def get_products(product_service: ProductService = Depends(ProductService)):
    return product_service.get_all_products()

@router.get("/{product_id}")
async def get_product(product_id: int, product_service: ProductService = Depends(ProductService)):
    product = product_service.get_product(product_id)
    if product:
        return product
    return {"error": "Product not found"}