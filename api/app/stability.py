# api/app/stability.py — генерация картинки (английский промпт)
import os
import httpx


STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
CORE_URL  = "https://api.stability.ai/v2beta/stable-image/generate/core"
ULTRA_URL = "https://api.stability.ai/v2beta/stable-image/generate/ultra"

# Допустимые AR на всякий
_ALLOWED_AR = {"1:1","16:9","9:16","3:2","2:3","4:3","3:4","5:4","4:5","21:9"}


async def generate_image_english(prompt_en: str) -> bytes:
    assert STABILITY_API_KEY, "STABILITY_API_KEY is missing"
    headers = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    }
    form = {
        "prompt": prompt_en,
        "output_format": "png",
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(ULTRA_URL, headers=headers, data=form)
        r.raise_for_status()
        return r.content # PNG bytes