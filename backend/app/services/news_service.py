from fastapi import HTTPException, status
import requests

from app.config import settings


def search_news(topic: str, page_size: int = 8) -> list[dict]:
    api_key = settings.news_api_key.strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="NEWS_API_KEY not configured")

    resp = requests.get(
        "https://newsapi.org/v2/everything",
        params={"q": topic, "sortBy": "publishedAt", "language": "en", "pageSize": page_size, "apiKey": api_key},
        timeout=20,
    )
    if resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="News API request failed")

    data = resp.json()
    return [
        {
            "title": article.get("title", ""),
            "source": (article.get("source") or {}).get("name", ""),
            "published_at": article.get("publishedAt", ""),
            "url": article.get("url", ""),
        }
        for article in data.get("articles", [])
    ]


def get_exchange_rates(base_currency: str = "USD", symbols: str = "INR,EUR") -> dict:
    api_key = settings.exchange_api_key.strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="EXCHANGE_API_KEY not configured")

    resp = requests.get(
        "https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}".format(api_key=api_key, base=base_currency),
        timeout=20,
    )
    if resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Exchange API request failed")

    data = resp.json()
    allowed = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    rates = data.get("conversion_rates", {}) or {}
    return {"base_currency": base_currency.upper(), "rates": {k: rates.get(k) for k in allowed if k in rates}}
