from typing import List, Dict, Any
from backend.app.services.product_service import ProductService
from backend.app.services.cart_service import CartService


class ToolCallHandler:
    def __init__(self, product_service: ProductService, cart_service: CartService):
        self.tool_outputs: List[Dict[str, str]] = []
        self.product_service = product_service
        self.cart_service = cart_service

    def handle_tool_call(self, tool_call: Any) -> None:
        if tool_call.function.name == "get_product_info":
            product_info = self.get_product_info(tool_call.function.arguments)
            self.tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": product_info
            })
        elif tool_call.function.name == "update_cart":
            result = self.update_cart(tool_call.function.arguments)
            self.tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": result
            })
        elif tool_call.function.name == "search_products":
            search_results = self.search_products(tool_call.function.arguments)
            self.tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": search_results
            })
        elif tool_call.function.name == "get_cart_summary":
            cart_summary = self.get_cart_summary()
            self.tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": cart_summary
            })

    def get_product_info(self, arguments: Dict[str, Any]) -> str:
        product_id = arguments.get("product_id")
        product = self.product_service.get_product(product_id)
        if product:
            return f"Product: {product.name}, Price: ${product.price}, Description: {product.description}"
        return "Product not found"

    def update_cart(self, arguments: Dict[str, Any]) -> str:
        product_id = arguments.get("product_id")
        quantity = arguments.get("quantity", 1)
        action = arguments.get("action", "add")
        
        if action == "add":
            self.cart_service.add_to_cart(product_id, quantity)
            return f"Added {quantity} of product {product_id} to cart"
        elif action == "remove":
            self.cart_service.remove_from_cart(product_id, quantity)
            return f"Removed {quantity} of product {product_id} from cart"
        
        return "Invalid action"

    def search_products(self, arguments: Dict[str, Any]) -> str:
        query = arguments.get("query", "")
        category = arguments.get("category", "")
        products = self.product_service.search_products(query, category)
        return ", ".join([f"{p.name} (${p.price})" for p in products[:5]])

    def get_cart_summary(self) -> str:
        cart = self.cart_service.get_cart()
        total = sum(item.product.price * item.quantity for item in cart.items)
        return f"Cart: {len(cart.items)} items, Total: ${total:.2f}"

    def get_tool_outputs(self) -> List[Dict[str, str]]:
        return self.tool_outputs