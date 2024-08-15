from openai import OpenAI
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.services.product_service import ProductService
from backend.app.services.cart_service import CartService
from backend.app.core.config import settings
import logging
from openai import AssistantEventHandler


class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    thread_id: str
    messages: List[Message]


class ChatEventHandler(AssistantEventHandler):
    def __init__(self, handle_chunk_func):
        self.handle_chunk_func = handle_chunk_func

    def on_text_created(self, text):
        self.handle_chunk_func({"type": "start", "content": ""})

    def on_text_delta(self, delta, snapshot):
        self.handle_chunk_func({"type": "stream", "content": delta.value})

    def on_tool_call_created(self, tool_call):
        self.handle_chunk_func({"type": "tool_call", "content": str(tool_call)})

    def on_tool_call_delta(self, delta, snapshot):
        self.handle_chunk_func({"type": "tool_call_delta", "content": str(delta)})

    def on_end(self):
        self.handle_chunk_func({"type": "end", "content": ""})



class AIService:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.model = model
        self.assistant_id = settings.ASSISTANT_ID  # Changed from OPENAI_ASSISTANT_ID
        self.product_service = ProductService()
        self.cart_service = CartService()
        self.get_or_create_assistant()

    def get_or_create_assistant(self):
        if self.assistant_id:
            try:
                self.assistant = self.client.beta.assistants.retrieve(self.assistant_id)
                logging.info(f"Using existing assistant with ID: {self.assistant_id}")
            except Exception as e:
                logging.warning(f"Failed to retrieve assistant with ID {self.assistant_id}. Creating a new one.")
                self.create_new_assistant()
        else:
            logging.info("No assistant ID provided. Creating a new assistant.")
            self.create_new_assistant()

    def create_new_assistant(self):
        assistant = self.create_assistant(
            name="eShop Assistant",
            instructions="You are an AI assistant for an e-commerce platform. Help users find products, manage their cart, and answer questions about the shopping process.",
            tools=self.default_tools()
        )
        self.assistant_id = assistant.id
        self.assistant = assistant
        logging.info(f"Created new assistant with ID: {self.assistant_id}")
        # You might want to update the ASSISTANT_ID in your .env file here
            # You might want to save this ID to your configuration or database for future use

    def create_assistant(self, name: str, instructions: str, tools: Optional[List[Dict[str, Any]]] = None):
        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools or self.default_tools(),
            model=self.model
        )
        return assistant

    def default_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "Get information about a specific product",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "The ID of the product"}
                        },
                        "required": ["product_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_cart",
                    "description": "Add or remove items from the cart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "The ID of the product"},
                            "quantity": {"type": "integer", "description": "The quantity to add or remove"},
                            "action": {"type": "string", "enum": ["add", "remove"], "description": "Whether to add or remove the item"}
                        },
                        "required": ["product_id", "quantity", "action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"},
                            "category": {"type": "string", "description": "The category to search in (optional)"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cart_summary",
                    "description": "Get a summary of the current cart",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

    def create_thread(self):
        return self.client.beta.threads.create()

    def add_message_to_thread(self, thread_id: str, role: str, content: str):
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )

    def run_assistant(self, thread_id: str, instructions: str = None, event_handler=None):
        if event_handler:
            chat_event_handler = ChatEventHandler(event_handler)
            return self.stream_run(thread_id, instructions, chat_event_handler)
        else:
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                instructions=instructions
            )
            return run

    def get_run_status(self, thread_id: str, run_id: str):
        return self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

    def get_messages(self, thread_id: str):
        return self.client.beta.threads.messages.list(thread_id=thread_id)

    def stream_run(self, thread_id: str, instructions: str, event_handler):
        with self.client.beta.threads.runs.create_and_stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            instructions=instructions,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()
            return stream.get_final_run()

    def update_assistant_context(self, thread_id: str):
        cart_summary = self.get_cart_summary()
        recent_products = self.get_recent_products()
        
        context_message = f"""
        Current cart summary: {cart_summary}
        Recently viewed products: {recent_products}
        Please consider this information when assisting the user.
        """
        
        self.add_message_to_thread(thread_id, "system", context_message)

    def get_cart_summary(self) -> str:
        cart = self.cart_service.get_cart()
        total = sum(item.product.price * item.quantity for item in cart.items)
        return f"Cart contains {len(cart.items)} items. Total: ${total:.2f}"

    def get_recent_products(self, limit: int = 5) -> str:
        recent_products = self.product_service.get_recent_products(limit)
        return ", ".join([f"{p.name} (${p.price})" for p in recent_products])

    def handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        tool_outputs = []
        for tool_call in tool_calls:
            if tool_call.function.name == "get_product_info":
                output = self.get_product_info(tool_call.function.arguments)
            elif tool_call.function.name == "update_cart":
                output = self.update_cart(tool_call.function.arguments)
            elif tool_call.function.name == "search_products":
                output = self.search_products(tool_call.function.arguments)
            elif tool_call.function.name == "get_cart_summary":
                output = self.get_cart_summary()
            else:
                output = "Unsupported tool call"
            
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": output
            })
        return tool_outputs

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

class ConversationManager:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.conversations: Dict[str, Conversation] = {}

    def start_conversation(self) -> str:
        thread = self.ai_service.create_thread()
        conversation = Conversation(thread_id=thread.id, messages=[])
        self.conversations[thread.id] = conversation
        return thread.id

    def add_message(self, thread_id: str, role: str, content: str):
        self.ai_service.add_message_to_thread(thread_id, role, content)
        message = Message(role=role, content=content)
        self.conversations[thread_id].messages.append(message)

    def get_conversation(self, thread_id: str) -> Optional[Conversation]:
        return self.conversations.get(thread_id)

    def run_conversation(self, thread_id: str, instructions: str = None, event_handler=None):
        self.ai_service.update_assistant_context(thread_id)
        
        if event_handler:
            return self.ai_service.stream_run(thread_id, instructions, event_handler)
        else:
            run = self.ai_service.run_assistant(thread_id, instructions)
            while True:
                status = self.ai_service.get_run_status(thread_id, run.id)
                if status.status == 'completed':
                    break
                elif status.status == 'requires_action':
                    tool_outputs = self.ai_service.handle_tool_calls(status.required_action.submit_tool_outputs.tool_calls)
                    self.ai_service.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
            messages = self.ai_service.get_messages(thread_id)
            for message in messages.data:
                if message.role == "assistant":
                    self.conversations[thread_id].messages.append(
                        Message(role="assistant", content=message.content[0].text.value)
                    )
            return self.conversations[thread_id]