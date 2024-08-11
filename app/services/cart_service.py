from typing import List, Dict

class CartService:
    def __init__(self):
        self.cart = {}

    def add_to_cart(self, product_id: int, quantity: int = 1):
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity

    def remove_from_cart(self, product_id: int):
        if product_id in self.cart:
            del self.cart[product_id]

    def get_cart(self) -> Dict[int, int]:
        return self.cart

    def clear_cart(self):
        self.cart.clear()