from typing import List, Dict

class ProductService:
    def __init__(self):
        # Simulace databáze produktů
        self.products = {
            1: {"id": 1, "name": "Product 1", "price": 10.99},
            2: {"id": 2, "name": "Product 2", "price": 15.99},
        }

    def get_product(self, product_id: int) -> Dict:
        return self.products.get(product_id)

    def get_all_products(self) -> List[Dict]:
        return list(self.products.values())