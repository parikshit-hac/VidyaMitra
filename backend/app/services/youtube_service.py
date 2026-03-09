from fastapi import HTTPException, status
import requests

from app.config import settings


def search_youtube(query: str, max_results: int = 6) -> list[dict]:
    api_key = settings.youtube_api_key.strip() or settings.google_api_key.strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="YOUTUBE_API_KEY not configured")

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
    }
    resp = requests.get(url, params=params, timeout=20)
    if resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="YouTube API request failed")

    data = resp.json()
    items: list[dict] = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        if not video_id:
            continue
        items.append(
            {
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "description": snippet.get("description", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )
    return items


def search_google_resources(query: str, num: int = 6) -> list[dict]:
    api_key = settings.google_api_key.strip()
    cse_id = settings.google_cse_id.strip()
    if not api_key or not cse_id:
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cse_id, "q": query, "num": num}
    resp = requests.get(url, params=params, timeout=20)
    if resp.status_code >= 400:
        return []

    data = resp.json()
    return [
        {
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "url": item.get("link", ""),
        }
        for item in data.get("items", [])
    ]
