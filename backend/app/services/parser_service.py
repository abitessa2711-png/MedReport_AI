"""
Turns raw OCR text into structured rows: test name, value, unit,
reference range.

This is intentionally rule-based (regex/heuristics) rather than another
AI call, per the required architecture:

    OCR -> Structured JSON -> Validation -> AI Summary Generation

Lab reports vary a lot in layout, so the parser tries several patterns
per line and only keeps a row when it can find at least a plausible
test name and a numeric-looking value. It never invents a reference
range that wasn't present in the text.
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

# A line printed by most lab report tables looks like one of:
#   Hemoglobin        10.2   g/dL      12-16
#   Hemoglobin | 10.2 | g/dL | 12-16
#   Glucose (Fasting)   118 mg/dL   70 - 100
#   WBC   7,500  cells/uL   4,000-11,000
#
# Loose grammar, in order:
#   1. test name        -> letters, spaces, parentheses, %, /
#   2. value             -> a number (possibly with commas/decimal)
#   3. unit              -> optional, short alphanumeric/µ token cluster
#   4. reference range   -> optional, "low-high", "<x", ">x", or "low - high"

LINE_SPLIT_RE = re.compile(r"\s*\|\s*|\t+|\s{2,}")

VALUE_RE = re.compile(r"^[\+\-]?\d[\d,]*\.?\d*$")

RANGE_RE = re.compile(
    r"(?:(?P<low>\d[\d,]*\.?\d*)\s*-\s*(?P<high>\d[\d,]*\.?\d*))"
    r"|(?P<cmp><|>|≤|≥)\s*(?P<bound>\d[\d,]*\.?\d*)"
)

UNIT_HINT_RE = re.compile(
    r"^[a-zA-Zµ%/³\.]+[a-zA-Zµ%/³\.0-9]*$"
)

DATE_RE = re.compile(
    r"(?P<date>\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}|"
    r"\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})",
    re.IGNORECASE,
)

DATE_LABEL_RE = re.compile(r"(report\s*date|collected|collection\s*date|date)", re.IGNORECASE)

# Lines that are clearly headers/noise, not test rows.
NOISE_LINE_RE = re.compile(
    r"^(test|parameter|investigation|value|result|unit|units|reference|range|"
    r"normal|remarks|method|specimen|patient|name|age|sex|gender|lab|"
    r"laboratory|hospital|address|doctor|dr\.?|page|report)\b",
    re.IGNORECASE,
)


@dataclass
class ParsedRow:
    test_name: str
    value: Optional[str] = None
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None


@dataclass
class ParsedReport:
    report_date: Optional[str] = None
    rows: List[ParsedRow] = field(default_factory=list)


def _to_float(token: Optional[str]) -> Optional[float]:
    if not token:
        return None
    try:
        return float(token.replace(",", ""))
    except ValueError:
        return None


def _find_report_date(lines: List[str]) -> Optional[str]:
    for line in lines:
        if DATE_LABEL_RE.search(line):
            m = DATE_RE.search(line)
            if m:
                return m.group("date")
    # fall back: first date-like token anywhere in the document
    for line in lines:
        m = DATE_RE.search(line)
        if m:
            return m.group("date")
    return None


def _parse_line(line: str) -> Optional[ParsedRow]:
    line = line.strip()
    if not line or NOISE_LINE_RE.match(line):
        return None

    tokens = [t.strip() for t in LINE_SPLIT_RE.split(line) if t.strip()]
    if len(tokens) < 2:
        # try splitting on single spaces as a last resort for tightly OCR'd lines
        tokens = [t for t in line.split(" ") if t]
        if len(tokens) < 2:
            return None

    # Find the first token that looks like a numeric value -> that's our anchor.
    value_idx = None
    for i, tok in enumerate(tokens):
        cleaned = tok.replace(",", "")
        if VALUE_RE.match(cleaned) and i > 0:
            value_idx = i
            break

    if value_idx is None:
        return None

    test_name = " ".join(tokens[:value_idx]).strip(" :-")
    if len(test_name) < 2:
        return None

    value_token = tokens[value_idx]
    remaining = tokens[value_idx + 1 :]

    unit = None
    reference_range = None

    for tok in remaining:
        if reference_range is None and RANGE_RE.search(tok):
            reference_range = tok
            continue
        if unit is None and UNIT_HINT_RE.match(tok) and not VALUE_RE.match(tok):
            unit = tok

    # Reference range sometimes spans multiple trailing tokens, e.g. "12 - 16"
    if reference_range is None and remaining:
        joined_tail = " ".join(remaining)
        m = RANGE_RE.search(joined_tail)
        if m:
            reference_range = m.group(0)

    return ParsedRow(
        test_name=test_name,
        value=value_token,
        numeric_value=_to_float(value_token),
        unit=unit,
        reference_range=reference_range,
    )


def parse_report_text(raw_text: str) -> ParsedReport:
    lines = [l for l in raw_text.splitlines() if l.strip()]
    report_date = _find_report_date(lines)

    rows: List[ParsedRow] = []
    for line in lines:
        row = _parse_line(line)
        if row:
            rows.append(row)

    return ParsedReport(report_date=report_date, rows=rows)
