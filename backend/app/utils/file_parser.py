import io
import re
from pathlib import Path
from uuid import UUID, uuid4

import pdfplumber


def sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", filename.strip())
    return cleaned or "resume.pdf"


def save_uploaded_pdf(file_bytes: bytes, original_filename: str, user_id: UUID) -> str:
    base_dir = Path(__file__).resolve().parents[2] / "uploads" / str(user_id)
    base_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(original_filename)
    final_name = f"{uuid4()}_{filename}"
    full_path = base_dir / final_name
    full_path.write_bytes(file_bytes)
    return str(full_path)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()
