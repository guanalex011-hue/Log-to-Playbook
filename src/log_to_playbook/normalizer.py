from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Normalize common log formatting noise while preserving useful content."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()
