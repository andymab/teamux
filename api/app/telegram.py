# api/app/telegram.py — публикация в Telegram
import os
import httpx
from typing import Optional


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT = os.getenv("TELEGRAM_CHAT_ID")
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def send_message(text: str, chat_id: Optional[str] = None) -> dict:
    assert BOT_TOKEN, "TELEGRAM_BOT_TOKEN is missing"
    payload = {"chat_id": chat_id or DEFAULT_CHAT, "text": text, "parse_mode": "HTML"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{BASE}/sendMessage", json=payload)
        r.raise_for_status()
        return r.json()


async def send_photo(png_bytes: bytes, caption: str = "", chat_id: Optional[str] = None) -> dict:
    assert BOT_TOKEN, "TELEGRAM_BOT_TOKEN is missing"
    chat = chat_id or DEFAULT_CHAT
    files = {"photo": ("image.png", png_bytes, "image/png")}
    data = {"chat_id": chat, "caption": caption}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{BASE}/sendPhoto", files=files, data=data)
        r.raise_for_status()
        return r.json()