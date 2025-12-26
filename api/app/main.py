# api/app/main.py — FastAPI маршруты

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from .deps import setup_cors, require_token
from .fetcher import fetch_and_extract
from .groq_client import analyze_text
# from .stability import generate_image_english
from .telegram import send_message, send_photo
from .post_builder import build_post

from .image_gen_stability import (
    generate_image_bytes_stability,
    StabilityAuthError, StabilityBillingError,
    StabilityRateLimitError, StabilityTemporaryError, StabilityBadRequest
)

import json

app = FastAPI(title="teamux API")
setup_cors(app)

class PostBuildBody(BaseModel):
    summary: str
    utm: str
    source_url: str | None = None
    model: str | None = None


class AnalyzeBody(BaseModel):
    text: str
    model: Optional[str] = None
    prompt: Optional[str] = None  # Новое поле для кастомного промта
    utm: Optional[str] = ""  # UTM метка
    site: Optional[str] = ""  # Сайт для ссылки


class AnalyzeUrlBody(BaseModel):
    url: str
    model: Optional[str] = None
    prompt: Optional[str] = None  # Новое поле для кастомного промта
    utm: Optional[str] = ""  # UTM метка  
    site: Optional[str] = ""  # Сайт для ссылки


class PublishBody(BaseModel):
    text: str


class ImageBody(BaseModel):
    prompt_en: str = Field(..., min_length=3, max_length=4000)
    engine: str | None = "core"           # "core" | "ultra"
    aspect_ratio: str | None = "1:1"       # "1:1","16:9","9:16","3:2","2:3"
    negative_prompt: str | None = None
    seed: int | None = None
    return_base64: bool | None = False     # если нужно вернуть картинку на фронт


class IChingBody(BaseModel):
    histogram: str = Field(..., example="100101111")
    model: Optional[str] = None

def normalize_histogram(value: str) -> tuple[str, str]:
    clean = value.replace(" ", "")
    if any(c not in "01" for c in clean):
        raise HTTPException(400, "Histogram must contain only 0 or 1")

    if len(clean) == 6:
        return clean, "classic"

    if len(clean) == 9:
        return clean, "extended"

    raise HTTPException(
        status_code=400,
        detail="Histogram must be 6 (classic) or 9 (extended) bits"
    )


ICHING_PROMPT_CLASSIC = """
Ты — знаток «Книги Перемен» (И Цзин).

Передана классическая гексаграмма из 6 линий (снизу вверх, 0 — инь, 1 — ян).

Гексаграмма: {histogram}

Верни строго валидный JSON с полями:
{{
  "type": "classic",
  "hexagram": "Название гексаграммы",
  "summary": "Краткое толкование",
  "article": "Развернутый комментарий",
  "advice": "Практический совет"
}}
Язык: русский.
"""


ICHING_PROMPT_EXTENDED = """
Ты — знаток «Книги Перемен» (И Цзин).

Передана расширенная гистограмма из 9 бит.
Каждые 3 бита образуют триграмму:

- первые 3 — ПРОШЛОЕ (основание ситуации)
- вторые 3 — НАСТОЯЩЕЕ (текущий процесс)
- третьи 3 — БУДУЩЕЕ (направление изменений)

Гистограмма: {histogram}

Интерпретируй три состояния как единый процесс изменений.

Верни СТРОГО валидный JSON:
{{
  "type": "extended",
  "past": {{ "trigram": "", "meaning": "" }},
  "present": {{ "trigram": "", "meaning": "" }},
  "future": {{ "trigram": "", "meaning": "" }},
  "article": "Целостная статья",
  "advice": "Практический совет"
}}

Язык: русский.
Стиль: философский, без мистики.
"""

@app.post("/iching")
async def iching(body: IChingBody):
    try:
        histogram, mode = normalize_histogram(body.histogram)
        model = body.model or "llama-3.3-70b-versatile"

        if mode == "classic":
            prompt = ICHING_PROMPT_CLASSIC.format(histogram=histogram)
        else:
            prompt = ICHING_PROMPT_EXTENDED.format(histogram=histogram)

        raw = await analyze_text(
            content="",
            model=model,
            custom_prompt=prompt
        )

        # return {
        #     "ok": True,
        #     "histogram": histogram,
        #     "raw_text": raw["text"],
        #     "usage": raw.get("usage", {}),
        #     "model": raw.get("model", model)
        # }

        text = raw["text"]

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=502,
                detail="Model returned invalid JSON"
            )

        return {
            "ok": True,
            "histogram": histogram,
            "result": result,
            "usage": raw.get("usage", {}),
            "model": raw.get("model", model),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/post/build")
async def post_build(body: PostBuildBody, _=Depends(require_token)):
    try:
        site = os.getenv("TEAMUX_SITE", "https://teamux.ru")
        result = await build_post(summary=body.summary, utm=body.utm, site=site, source_url=body.source_url, model=body.model)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/analyze")
async def post_analyze(body: AnalyzeBody, _=Depends(require_token)):
    try:
        result = await build_post(
            summary=body.text,
            utm=body.utm or "",
            site=body.site or "",
            source_url=None,
            model=body.model,
            custom_prompt=body.prompt  # Передаем кастомный промт если есть
        )
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/analyze-url")
async def post_analyze_url(body: AnalyzeUrlBody, _=Depends(require_token)):
    try:
        content = await fetch_and_extract(body.url)
        
        # Если нужен промт из URL, можно добавить так:
        # prompt_content = await fetch_and_extract(body.prompt_url) if body.prompt_url else body.prompt
        
        result = await build_post(
            summary=content,
            utm=body.utm or "",
            site=body.site or "",
            source_url=body.url,  
            model=body.model,
            custom_prompt=body.prompt
        )
        
        return {"source": body.url, **result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/publish")
async def post_publish(body: PublishBody, _=Depends(require_token)):
    try:
        res = await send_message(body.text)
        return res
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/image")
async def post_image(body: ImageBody, _=Depends(require_token)):
    try:
        png = await generate_image_bytes_stability(
            prompt=body.prompt_en,
            engine="core", #body.engine or "ultra",
            aspect_ratio=body.aspect_ratio or "1:1",
            output_format="png",
            seed=body.seed,
            negative_prompt=body.negative_prompt,
        )

        # 👉 отправка в Telegram как и раньше (если нужно)
        await send_photo(png, caption=body.prompt_en)

        if body.return_base64:
            import base64
            b64 = base64.b64encode(png).decode()
            return {"ok": True, "image_base64": f"data:image/png;base64,{b64}"}

        return {"ok": True}

    except StabilityAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except StabilityBillingError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except StabilityRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except StabilityTemporaryError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except StabilityBadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"ok": True}