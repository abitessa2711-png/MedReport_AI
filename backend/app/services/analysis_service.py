"""
Compares each extracted test value against the reference range that was
actually printed on the report. Never invents a reference range - if the
report didn't provide one, the status is "Unknown", not a guess.
"""
import re
from typing import Optional

from app.services.parser_service import RANGE_RE


def determine_status(numeric_value: Optional[float], reference_range: Optional[str]) -> str:
    if numeric_value is None:
        return "Unknown"
    if not reference_range:
        return "Unknown"

    m = RANGE_RE.search(reference_range)
    if not m:
        return "Unknown"

    if m.group("low") is not None and m.group("high") is not None:
        low = float(m.group("low").replace(",", ""))
        high = float(m.group("high").replace(",", ""))
        if numeric_value < low:
            return "Low"
        if numeric_value > high:
            return "High"
        return "Normal"

    if m.group("cmp") and m.group("bound") is not None:
        bound = float(m.group("bound").replace(",", ""))
        cmp = m.group("cmp")
        if cmp in ("<", "≤"):
            return "Normal" if numeric_value <= bound else "High"
        if cmp in (">", "≥"):
            return "Normal" if numeric_value >= bound else "Low"

    return "Unknown"
