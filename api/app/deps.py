# api/app/deps.py — конфиг и CORS
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Header, HTTPException



def setup_cors(app: FastAPI):
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,https://teamux-news.355042.ru").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

API_TOKEN = os.getenv("API_TOKEN")

async def require_token(authorization: str = Header(default="")):
    # если токен не задан — пропускаем (удобно в dev)
    if not API_TOKEN:
        return
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")