from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.app.api import products, cart
from backend.app.api.routes import chat
from backend.app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Připojení routerů
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])

@app.get("/")
async def root():
    return FileResponse("frontend/dist/index.html")

# Servírování statických souborů
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    routes = [route.path for route in app.routes]
    print(f"Registered routes: {routes}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)