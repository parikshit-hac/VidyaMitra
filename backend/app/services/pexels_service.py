from fastapi import HTTPException, status
import requests

from app.config import settings


def search_images(query: str, per_page: int = 8) -> list[dict]:
    api_key = settings.pexels_api_key.strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PEXELS_API_KEY not configured")

    resp = requests.get(
        "https://api.pexels.com/v1/search",
        params={"query": query, "per_page": per_page},
        headers={"Authorization": api_key},
        timeout=20,
    )
    if resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Pexels API request failed")

    data = resp.json()
    images: list[dict] = []
    for photo in data.get("photos", []):
        src = photo.get("src", {})
        images.append(
            {
                "id": photo.get("id"),
                "photographer": photo.get("photographer"),
                "page_url": photo.get("url"),
                "image_url": src.get("large") or src.get("original"),
                "thumb_url": src.get("medium"),
            }
        )
    return images
