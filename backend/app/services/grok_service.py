import json
import re

from fastapi import HTTPException, status
from groq import Groq
from groq import APIConnectionError as GroqConnectionError
from groq import APIStatusError as GroqStatusError
from groq import RateLimitError as GroqRateLimitError

from app.config import settings


def _provider_config() -> tuple[str, str, str]:
    api_key = settings.groq_api_key.strip() or settings.grok_api_key.strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GROQ_API_KEY not configured")
    model_name = (
        settings.groq_model.strip()
        or settings.grok_model.strip()
        or "llama-3.1-8b-instant"
    )
    base_url = (
        settings.groq_base_url.strip()
        or settings.grok_base_url.strip()
        or "https://api.groq.com/openai/v1"
    )
    # Groq SDK already appends /openai/v1 internally.
    # Normalize user-provided URL to avoid duplicated path.
    normalized = base_url.rstrip("/")
    if normalized.endswith("/openai/v1"):
        normalized = normalized[: -len("/openai/v1")]
    if normalized.endswith("/openai"):
        normalized = normalized[: -len("/openai")]
    if not normalized:
        normalized = "https://api.groq.com"
    return api_key, model_name, normalized


def generate_career_support(prompt: str) -> str:
    api_key, model_name, base_url = _provider_config()
    client = Groq(api_key=api_key, base_url=base_url)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are VidyaMitra AI assistant. Be concise, practical, and structured."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
    except GroqRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Groq quota exceeded. {str(exc)[:400]}",
        ) from exc
    except GroqConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq connection failed. {str(exc)[:400]}",
        ) from exc
    except GroqStatusError as exc:
        code = getattr(exc, "status_code", None) or status.HTTP_502_BAD_GATEWAY
        mapped = status.HTTP_401_UNAUTHORIZED if int(code) in (401, 403) else status.HTTP_502_BAD_GATEWAY
        raise HTTPException(
            status_code=mapped,
            detail=f"Groq API error ({code}). {str(exc)[:400]}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq unexpected error. {str(exc)[:400]}",
        ) from exc

    output = str((response.choices[0].message.content if response.choices else "") or "").strip()
    if not output:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Groq returned an empty response.")
    return output


def _extract_json_object(text: str) -> dict | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    if "```" in text:
        cleaned = text.replace("```json", "```")
        blocks = re.findall(r"```(.*?)```", cleaned, flags=re.DOTALL)
        for block in blocks:
            candidate = block.strip()
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None
    return None


def generate_json(prompt: str) -> dict:
    api_key, model_name, base_url = _provider_config()
    client = Groq(api_key=api_key, base_url=base_url)

    strict_prompt = (
        f"{prompt}\n\nReturn only a valid JSON object. No markdown, no explanation, no extra text."
    )
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You must return strict JSON object output only."},
                {"role": "user", "content": strict_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = str((response.choices[0].message.content if response.choices else "") or "").strip()
    except Exception:
        content = generate_career_support(strict_prompt)

    parsed = _extract_json_object(content)
    if parsed is not None:
        return parsed

    retry = generate_career_support(
        "Convert the following into strict JSON object only, no text:\n"
        f"{content}"
    )
    parsed_retry = _extract_json_object(retry)
    if parsed_retry is not None:
        return parsed_retry

    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Groq returned non-JSON response.")
