from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import chat

app = FastAPI()

# Nastavení CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Nastavte podle vašich potřeb
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zahrnutí routerů
app.include_router(chat.router)
app.include_router(cart.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)