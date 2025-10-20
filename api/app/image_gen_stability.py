# image_gen_stability.py
"""
Адаптер для Stability AI: Stable Image Core / Ultra.
Генерирует изображение и возвращает байты.
"""

import os
import httpx

STABILITY_KEY_ENV = "STABILITY_API_KEY"
CORE_URL  = "https://api.stability.ai/v2beta/stable-image/generate/core"
ULTRA_URL = "https://api.stability.ai/v2beta/stable-image/generate/ultra"

# Допустимые aspect_ratio: "1:1","16:9","9:16","3:2","2:3"
VALID_AR = {"1:1", "16:9", "9:16", "3:2", "2:3"}


class StabilityAuthError(RuntimeError): ...
class StabilityBillingError(RuntimeError): ...
class StabilityRateLimitError(RuntimeError): ...
class StabilityTemporaryError(RuntimeError): ...
class StabilityBadRequest(RuntimeError): ...


def _get_key() -> str:
    key = os.getenv(STABILITY_KEY_ENV)
    if not key:
        raise RuntimeError(f"{STABILITY_KEY_ENV} is not set")
    return key


def _endpoint(engine: str) -> str:
    e = (engine or "core").lower()
    if e not in {"core", "ultra"}:
        e = "core"
    return CORE_URL if e == "core" else ULTRA_URL


def _sanitize_prompt(p: str) -> str:
    p = (p or "").strip()
    if not p:
        p = "Minimalistic Tilda-style landing page, clean UX, large typography"
    return p[:4000]


async def generate_image_bytes_stability(
    prompt: str,
    *,
    engine: str = "core",          # "core" | "ultra"
    aspect_ratio: str = "16:9",    # "1:1","16:9","9:16","3:2","2:3"
    output_format: str = "png",    # "png" | "jpeg" | "webp"
    seed: int | None = None,
    negative_prompt: str | None = None,
) -> bytes:
    """
    Возвращает байты изображения. При ошибках биллинга/лимитов/авторизации кидает специализированные исключения.
    """
    key = _get_key()
    if aspect_ratio not in VALID_AR:
        aspect_ratio = "16:9"

    # ВАЖНО: используем multipart/form-data через `files=...`
    files = {
        "prompt": (None, _sanitize_prompt(prompt)),
        "aspect_ratio": (None, aspect_ratio),
        "output_format": (None, output_format),
    }
    if negative_prompt:
        files["negative_prompt"] = (None, negative_prompt)
    if seed is not None:
        files["seed"] = (None, str(seed))

    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "image/*, application/json",  # примем и байты, и JSON
    }

    url = _endpoint(engine)
    
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(url, headers=headers, files=files)

        ct = (r.headers.get("content-type") or "").lower()

        # 1) Идеальный случай — пришло изображение в бинаре
        if r.status_code == 200 and ct.startswith("image/"):
            return r.content

        # 2) Пришёл JSON (часто с base64)
        try:
            body = r.json()
        except Exception:
            body = {"error": {"message": r.text or f"HTTP {r.status_code}"}}

        # если есть base64 — декодируем
        b64 = None
        if isinstance(body, dict):
            b64 = body.get("image") or body.get("image_base64")
            if not b64 and isinstance(body.get("artifacts"), list) and body["artifacts"]:
                b64 = body["artifacts"][0].get("base64")

        if r.status_code == 200 and b64:
            import base64 as _b64
            return _b64.b64decode(b64)

        # иначе — это ошибка, разбираем и бросаем понятнее
        msg = (body.get("error") or {}).get("message") or body.get("message") or r.text or "Unknown error"

        if r.status_code in (401, 403):
            raise StabilityAuthError(msg)
        if r.status_code == 402:
            raise StabilityBillingError(msg)
        if r.status_code == 429:
            raise StabilityRateLimitError(msg)
        if r.status_code in (500, 502, 503):
            raise StabilityTemporaryError(msg)
        if r.status_code in (400, 422):
            raise StabilityBadRequest(msg)

        r.raise_for_status()
        raise RuntimeError(f"Stability error {r.status_code}: {msg}")