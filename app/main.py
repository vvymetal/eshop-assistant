from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Nastavení CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Připojení routerů
app.include_router(chat.router, prefix="/api")

# Kořenová cesta
@app.get("/")
async def root():
    return {"message": "Welcome to the E-shop Assistant API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)