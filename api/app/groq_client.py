# api/app/groq_client.py — обращение к Groq (OpenAI совместимый)

import os
import httpx


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


PROMPT_TEMPLATE = (
    """Проанализируй предоставленный текст и создай структурированную выжимку.\n\n"""
    "ТЕКСТ ДЛЯ АНАЛИЗА:\n{content}\n\n"
    "СОЗДАЙ ВЫЖИМКУ В ФОРМАТЕ:\n"
    "🎯 ОСНОВНАЯ ИДЕЯ: 1-2 предложения, суть текста\n"
    "📌 КЛЮЧЕВЫЕ ПУНКТЫ: 3-5 основных тезисов маркерами\n"
    "💡 ПРАКТИЧЕСКАЯ ПОЛЬЗА: как можно применить эту информацию\n"
    "👥 ЦЕЛЕВАЯ АУДИТОРИЯ: кому будет особенно интересно\n\n"
    "ТРЕБОВАНИЯ:\n- Объем: 400-700 символов\n- Ясный, деловой язык\n- Только важная информация, без воды\n- Сохрани основные факты и выводы"
)


async def analyze_text(content: str, model: str | None = None) -> dict:
    assert GROQ_API_KEY, "GROQ_API_KEY is missing"
    model = model or DEFAULT_MODEL


    # Подрежем на всякий случай ~12k символов
    content = (content[:12000] + "\n\n...[текст обрезан]") if len(content) > 12000 else content


    payload = {
    "model": model,
    "temperature": 0.7,
    "max_tokens": 800,
    "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(content=content)}],
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}


    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(GROQ_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return {"text": text, "usage": usage, "model": model}