# api/app/main.py — FastAPI маршруты

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
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


app = FastAPI(title="teamux API")
setup_cors(app)

class PostBuildBody(BaseModel):
    summary: str
    utm: str
    source_url: str | None = None
    model: str | None = None


class AnalyzeBody(BaseModel):
    text: str
    model: str | None = None


class AnalyzeUrlBody(BaseModel):
    url: str
    model: str | None = None


class PublishBody(BaseModel):
    text: str


class ImageBody(BaseModel):
    prompt_en: str = Field(..., min_length=3, max_length=4000)
    engine: str | None = "core"           # "core" | "ultra"
    aspect_ratio: str | None = "1:1"       # "1:1","16:9","9:16","3:2","2:3"
    negative_prompt: str | None = None
    seed: int | None = None
    return_base64: bool | None = False     # если нужно вернуть картинку на фронт


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
        result = await analyze_text(body.text, body.model)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/analyze-url")
async def post_analyze_url(body: AnalyzeUrlBody, _=Depends(require_token)):
    try:
        content = await fetch_and_extract(body.url)
        result = await analyze_text(content, body.model)
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