#api/app/fetcher.py — загрузка и извлечение текста по URL
import httpx
from readability import Document
from bs4 import BeautifulSoup


async def fetch_and_extract(url: str) -> str:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        html = r.text
    doc = Document(html)
    summary_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, "lxml")
    text = soup.get_text("\n", strip=True)
    return text