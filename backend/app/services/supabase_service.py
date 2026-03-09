import base64
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
import requests

from app.config import settings


def _headers(content_type: str = "application/json") -> dict[str, str]:
    # Prefer service role key for backend operations (bypasses RLS safely on server side).
    key = settings.supabase_service_role_key.strip() or settings.supabase_key.strip()
    if not settings.supabase_url.strip() or not key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase config missing")
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": content_type}


def _error_detail(resp: requests.Response, default_msg: str) -> str:
    body = (resp.text or "").strip().replace("\n", " ")
    if len(body) > 300:
        body = body[:300] + "..."
    return f"{default_msg}. Supabase status={resp.status_code}. body={body or 'empty'}"


def sync_profile_data(user_id: UUID, profile_data: dict) -> dict:
    base_url = settings.supabase_url.strip().rstrip("/")
    payload = {
        "profile_data": profile_data,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    resp = requests.patch(
        f"{base_url}/rest/v1/users?id=eq.{user_id}",
        params={"select": "id,email,name,profile_data,updated_at"},
        headers={**_headers(), "Prefer": "return=representation"},
        json=payload,
        timeout=20,
    )
    if resp.status_code >= 400:
        mapped = status.HTTP_403_FORBIDDEN if resp.status_code in (401, 403) else status.HTTP_502_BAD_GATEWAY
        raise HTTPException(status_code=mapped, detail=_error_detail(resp, "Supabase profile sync failed"))
    return {"synced": True, "user": (resp.json() or [{}])[0]}


def upload_file_base64(user_id: UUID, filename: str, content_base64: str, content_type: str, bucket: str | None) -> dict:
    bucket_name = (bucket or settings.supabase_bucket).strip()
    if not bucket_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supabase bucket name is empty")
    base_url = settings.supabase_url.strip().rstrip("/")
    try:
        raw = base64.b64decode(content_base64)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid base64 content") from exc

    object_path = f"{user_id}/{filename}"
    upload_url = f"{base_url}/storage/v1/object/{bucket_name}/{object_path}"
    resp = requests.post(
        upload_url,
        headers={**_headers(content_type=content_type), "x-upsert": "true"},
        data=raw,
        timeout=30,
    )
    if resp.status_code >= 400:
        if resp.status_code == 409:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_error_detail(resp, "File already exists"))
        if resp.status_code in (401, 403):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_error_detail(resp, "Supabase storage access denied"))
        if resp.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_error_detail(resp, "Supabase bucket not found"))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=_error_detail(resp, "Supabase file upload failed"))

    public_url = f"{base_url}/storage/v1/object/public/{bucket_name}/{object_path}"
    return {"uploaded": True, "bucket": bucket_name, "path": object_path, "public_url": public_url}


def get_recent_profile_updates(limit: int = 20) -> list[dict]:
    base_url = settings.supabase_url.strip().rstrip("/")
    resp = requests.get(
        f"{base_url}/rest/v1/users",
        params={
            "select": "id,email,name,profile_data,updated_at",
            "order": "updated_at.desc.nullslast",
            "limit": max(1, min(limit, 100)),
        },
        headers=_headers(),
        timeout=20,
    )
    if resp.status_code >= 400:
        mapped = status.HTTP_403_FORBIDDEN if resp.status_code in (401, 403) else status.HTTP_502_BAD_GATEWAY
        raise HTTPException(status_code=mapped, detail=_error_detail(resp, "Supabase realtime fetch failed"))
    return resp.json()
