# api/app/main.py — FastAPI маршруты

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .deps import setup_cors
from .fetcher import fetch_and_extract
from .groq_client import analyze_text
from .stability import generate_image_english
from .telegram import send_message, send_photo


app = FastAPI(title="teamux API")
setup_cors(app)


class AnalyzeBody(BaseModel):
    text: str
    model: str | None = None


class AnalyzeUrlBody(BaseModel):
    url: str
    model: str | None = None


class PublishBody(BaseModel):
    text: str


class ImageBody(BaseModel):
    prompt_en: str


@app.post("/analyze")
async def post_analyze(body: AnalyzeBody):
    try:
        result = await analyze_text(body.text, body.model)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/analyze-url")
async def post_analyze_url(body: AnalyzeUrlBody):
    try:
        content = await fetch_and_extract(body.url)
        result = await analyze_text(content, body.model)
        return {"source": body.url, **result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/publish")
async def post_publish(body: PublishBody):
    try:
        res = await send_message(body.text)
        return res
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/image")
async def post_image(body: ImageBody):
    try:
        png = await generate_image_english(body.prompt_en)
        # по желанию — сразу отправлять в Telegram
        await send_photo(png, caption=body.prompt_en)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))