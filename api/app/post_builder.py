import os
from pathlib import Path
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

TEMPLATES_DIR = Path(__file__).parent / "templates"
PROMPT_FILE = TEMPLATES_DIR / "prompt_tg_post_ru.txt"

def _load_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def _render_prompt(summary: str, utm: str, site: str, source_url: str | None) -> str:
    tpl = _load_prompt()
    # простая подстановка (без дополнительных зависимостей)
    prompt = (tpl
      .replace("{{summary}}", summary)
      .replace("{{utm}}", utm)
      .replace("{{site}}", site)
      .replace("{{#if source_url}}— Не указывать исходный текст.{{/if}}", "— Не указывать исходный текст." if source_url else "")
    )
    return prompt

async def build_post(summary: str, utm: str, site: str, source_url: str | None = None, model: str | None = None) -> dict:
    assert GROQ_API_KEY, "GROQ_API_KEY is missing"
    model = model or DEFAULT_MODEL
    prompt = _render_prompt(summary=summary, utm=utm, site=site, source_url=source_url)

    payload = {
        "model": model,
        "temperature": 0.5,
        "max_tokens": 600,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(GROQ_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()

    text = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage", {})
    return {"text": text, "usage": usage, "model": model}
