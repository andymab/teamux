# api/app/stability.py — генерация картинки (английский промпт)
import os
import httpx


STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/ultra"


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
        r = await client.post(STABILITY_URL, headers=headers, data=form)
        r.raise_for_status()
        return r.content # PNG bytes