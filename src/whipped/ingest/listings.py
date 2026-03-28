"""Parse unstructured listing text into a Listing."""
from __future__ import annotations

import re

from whipped.domain.models import Listing


def parse_listing(text: str) -> Listing:
    """Extract structured fields from free-text car listing."""
    # Stub: real implementation will use regex/LLM extraction
    return Listing(
        make=_extract_first(r"\b(ford|vauxhall|bmw|audi|toyota|honda|vw|mercedes)\b", text, "unknown"),
        model=_extract_first(r"(?:ford|vauxhall|bmw|audi|toyota|honda|vw|mercedes)\s+(\w+)", text, "unknown"),
        year=int(_extract_first(r"\b(20[0-2]\d|19[89]\d)\b", text, "2020")),
        mileage_miles=_extract_int(r"([\d,]+)\s*(?:miles|mi)", text),
        fuel_type=_extract_first(r"\b(petrol|diesel|hybrid|electric)\b", text),
        engine_size_l=_extract_float(r"(\d\.\d)\s*(?:l|litre)", text),
        price_gbp=_extract_int(r"[£$]([\d,]+)", text),
        raw_text=text,
    )


def _extract_first(pattern: str, text: str, default: str | None = None) -> str | None:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1) if m and m.lastindex else (m.group(0) if m else default)


def _extract_int(pattern: str, text: str) -> int | None:
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def _extract_float(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None
