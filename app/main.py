from fastapi import FastAPI
from app.api.routes import chat, products

app = FastAPI()

app.include_router(chat.router)
app.include_router(products.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Eshop Assistant"}