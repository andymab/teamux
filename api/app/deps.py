# api/app/deps.py — конфиг и CORS
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI



def setup_cors(app: FastAPI):
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )