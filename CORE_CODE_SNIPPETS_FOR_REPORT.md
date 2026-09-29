# MedReport AI — Core Implementation Code Snippets
**Academic Project Report — Chapter: Implementation & System Modules**

---

## 1. Module 1: Optical Character Recognition (OCR) Engine
**File:** `backend/app/services/ocr_service.py`  
**Purpose:** Pre-processes uploaded medical documents (rasterizes PDFs at 300 DPI via PyMuPDF, converts images to grayscale via Pillow), and extracts raw text using Tesseract OCR with an LSTM neural network (`--oem 3 --psm 6`).

```python
import io
import pytesseract
from PIL import Image

# Configured for structured tabular text extraction
TESSERACT_CONFIG = "--oem 3 --psm 6"

def _ocr_image(img: Image.Image) -> str:
    """Grayscale preprocessing enhances OCR contrast on clinical scan sheets."""
    img = img.convert("L")
    return pytesseract.image_to_string(img, config=TESSERACT_CONFIG)

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from digital layer or renders pages at 300 DPI for OCR."""
    import fitz  # PyMuPDF
    page_texts = []
    doc = fitz.open(file_path)
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        embedded_text = page.get_text("text")
        if embedded_text and embedded_text.strip():
            page_texts.append(embedded_text)
            continue
        # Fallback to high-resolution rasterization
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        page_texts.append(_ocr_image(img))
    doc.close()
    return "\n".join(t for t in page_texts if t and t.strip())
```

---

## 2. Module 2: Rule-Based Heuristic NLP Parser
**File:** `backend/app/services/parser_service.py`  
**Purpose:** Converts raw, unstructured OCR text lines into structured parameters (`test_name`, `value`, `unit`, `reference_range`) using regular expressions and anchor-based tokenization without LLM hallucination.

```python
import re
from dataclasses import dataclass
from typing import Optional

LINE_SPLIT_RE = re.compile(r"\s*\|\s*|\t+|\s{2,}")
VALUE_RE = re.compile(r"^[\+\-]?\d[\d,]*\.?\d*$")
RANGE_RE = re.compile(
    r"(?:(?P<low>\d[\d,]*\.?\d*)\s*-\s*(?P<high>\d[\d,]*\.?\d*))"
    r"|(?P<cmp><|>|≤|≥)\s*(?P<bound>\d[\d,]*\.?\d*)"
)
UNIT_HINT_RE = re.compile(r"^[a-zA-Zµ%/³\.]+[a-zA-Zµ%/³\.0-9]*$")

@dataclass
class ParsedRow:
    test_name: str
    value: Optional[str] = None
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None

def _parse_line(line: str) -> Optional[ParsedRow]:
    tokens = [t.strip() for t in LINE_SPLIT_RE.split(line) if t.strip()]
    if len(tokens) < 2:
        return None

    # Anchor detection: First numeric token is the lab measurement value
    value_idx = None
    for i, tok in enumerate(tokens):
        if VALUE_RE.match(tok.replace(",", "")) and i > 0:
            value_idx = i
            break

    if value_idx is None:
        return None

    test_name = " ".join(tokens[:value_idx]).strip(" :-")
    value_token = tokens[value_idx]
    remaining = tokens[value_idx + 1:]

    unit, reference_range = None, None
    for tok in remaining:
        if reference_range is None and RANGE_RE.search(tok):
            reference_range = tok
            continue
        if unit is None and UNIT_HINT_RE.match(tok) and not VALUE_RE.match(tok):
            unit = tok

    return ParsedRow(
        test_name=test_name,
        value=value_token,
        numeric_value=float(value_token.replace(",", "")),
        unit=unit,
        reference_range=reference_range
    )
```

---

## 3. Module 3: Clinical Decision Support System (CDSS) Status Classifier
**File:** `backend/app/services/analysis_service.py`  
**Purpose:** Deterministic boundary evaluation algorithm comparing parsed patient values against report-printed biological reference intervals. Never guesses or fabricates normal ranges.

```python
from typing import Optional
from app.services.parser_service import RANGE_RE

def determine_status(numeric_value: Optional[float], reference_range: Optional[str]) -> str:
    """
    Evaluates biomarker against biological thresholds:
    Returns: 'Normal' | 'Low' | 'High' | 'Unknown'
    """
    if numeric_value is None or not reference_range:
        return "Unknown"

    m = RANGE_RE.search(reference_range)
    if not m:
        return "Unknown"

    # Dual-bound range comparison: low - high (e.g., 70 - 99 mg/dL)
    if m.group("low") is not None and m.group("high") is not None:
        low = float(m.group("low").replace(",", ""))
        high = float(m.group("high").replace(",", ""))
        if numeric_value < low:
            return "Low"
        if numeric_value > high:
            return "High"
        return "Normal"

    # Single-bound threshold comparison: < bound or > bound (e.g., < 200 mg/dL)
    if m.group("cmp") and m.group("bound") is not None:
        bound = float(m.group("bound").replace(",", ""))
        cmp = m.group("cmp")
        if cmp in ("<", "≤"):
            return "Normal" if numeric_value <= bound else "High"
        if cmp in (">", "≥"):
            return "Normal" if numeric_value >= bound else "Low"

    return "Unknown"
```

---

## 4. Module 4: Condition-Specific Bilingual Advisory Engine
**File:** `backend/app/services/ai_service.py`  
**Purpose:** Maps specific abnormal biomarker groups (Diabetes, Dyslipidemia, Anemia, Renal, Hepatic, Thyroid) to clinically validated dietary and preventive care guidance in both English and Tamil.

```python
from typing import Any, Dict, List

def _generate_condition_specific_guidance(
    structured_results: List[Dict[str, Any]],
    abnormal: List[Dict[str, Any]]
) -> Dict[str, str]:
    en_lifestyle, ta_lifestyle = [], []
    en_prevention, ta_prevention = [], []

    abnormal_names = " ".join([r.get("test_name", "").lower() for r in abnormal])

    # 1. Diabetes / Glucose Regulation
    if any(k in abnormal_names for k in ["glucose", "sugar", "hba1c", "fbs", "ppbs"]):
        en_lifestyle.append("• Blood Sugar Focus: Prioritize low-glycemic index foods (millets, oats, leafy greens). Avoid refined sugars and white rice.")
        ta_lifestyle.append("• இரத்த சர்க்கரை வழிகாட்டல்: சிறுதானியங்கள், ஓட்ஸ், பச்சை காய்கறிகளை சேர்க்கவும். வெள்ளை சர்க்கரை, இனிப்புகள் தவிர்க்கவும்.")
        en_prevention.append("• Glycemic Monitoring: Test fasting blood sugar weekly. Schedule an HbA1c test every 3 months.")
        ta_prevention.append("• சர்க்கரை கண்காணிப்பு: வாரம் ஒருமுறை சர்க்கரை அளவை பரிசோதிக்கவும். 3 மாதங்களுக்கு ஒருமுறை HbA1c பரிசோதனை செய்யவும்.")

    # 2. Lipid Profile / Cardiovascular Wellness
    if any(k in abnormal_names for k in ["cholesterol", "triglyceride", "ldl", "lipid"]):
        en_lifestyle.append("• Heart Wellness: Reduce saturated fats, ghee, and deep-fried items. Add walnuts, almonds, and 40-min aerobic cardio.")
        ta_lifestyle.append("• இதய பாதுகாப்பு: நெய், பொரித்த உணவுகளை குறைக்கவும். பாதாம், வால்நட் சேர்த்து உடற்பயிற்சி செய்யவும்.")
        en_prevention.append("• Lipid Check: Retest lipid profile in 8-12 weeks. Monitor blood pressure periodically.")
        ta_prevention.append("• இதய பராமரிப்பு: 2-3 மாதங்களில் மீண்டும் Lipid Profile பரிசோதனை செய்யவும்.")

    # 3. Anemia / Hematology
    if any(k in abnormal_names for k in ["hemoglobin", "hb", "rbc", "iron", "ferritin"]):
        en_lifestyle.append("• Iron Nutrition: Consume moringa leaves, dates, raisins, pomegranate, and beetroot paired with Vitamin C.")
        ta_lifestyle.append("• ஹீமோகுளோபின் வழிகாட்டல்: முருங்கைக்கீரை, பேரீச்சம்பழம், மாதுளை, நெல்லிக்காய் அதிகம் சாப்பிடவும்.")
        en_prevention.append("• Anemia Tracking: Recheck Complete Blood Count (CBC) and serum ferritin in 6-8 weeks.")
        ta_prevention.append("• இரத்த சோகை கண்காணிப்பு: 6-8 வாரங்களில் மீண்டும் CBC பரிசோதனை செய்யவும்.")

    return {
        "lifestyle_en": "\n\n".join(en_lifestyle),
        "lifestyle_ta": "\n\n".join(ta_lifestyle),
        "prevention_en": "\n\n".join(en_prevention),
        "prevention_ta": "\n\n".join(ta_prevention),
    }
```

---

## 5. Module 5: FastAPI REST Analysis Controller
**File:** `backend/app/routers/analyze.py`  
**Purpose:** Coordinates user corrections, invokes the bilingual AI/CDSS layer, commits results to the database, and returns the serialized JSON response.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisResult, ExtractedResult, Report
from app.schemas.report_schemas import AnalyzeRequest, AnalyzeResponse
from app.services.ai_service import generate_bilingual_summary

router = APIRouter()

@router.post("/analyze-report", response_model=AnalyzeResponse)
def analyze_report(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == payload.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    rows = db.query(ExtractedResult).filter(ExtractedResult.report_id == report.id).all()
    
    # Transform validated rows into structured dictionary representation
    structured_results = [
        {
            "test_name": r.test_name,
            "value": r.value,
            "unit": r.unit,
            "reference_range": r.reference_range,
            "status": r.status,
        }
        for r in rows
    ]

    # Generate bilingual medical summary & targeted advice
    summary = generate_bilingual_summary(structured_results, age=payload.age, gender=payload.gender)

    # Persist analysis findings
    analysis = AnalysisResult(
        report_id=report.id,
        overall_summary_en=summary["overall_summary_en"],
        overall_summary_ta=summary["overall_summary_ta"],
        abnormal_findings_en=summary["abnormal_findings_en"],
        abnormal_findings_ta=summary["abnormal_findings_ta"],
        lifestyle_en=summary.get("lifestyle_en"),
        lifestyle_ta=summary.get("lifestyle_ta"),
        prevention_en=summary.get("prevention_en"),
        prevention_ta=summary.get("prevention_ta"),
        ai_provider=summary["ai_provider"],
        ai_model=summary["ai_model"],
    )
    db.add(analysis)
    report.status = "analyzed"
    db.commit()

    return AnalyzeResponse(report_id=report.id, status=report.status, extracted_results=rows, analysis=analysis)
```

---

## 6. Module 6: Frontend Data Visualization & Bilingual Dashboard
**File:** `frontend/src/components/Charts.jsx`  
**Purpose:** Recharts data visualization rendering comparison between patient values and safe reference thresholds.

```jsx
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts'

export default function ResultsChart({ rows }) {
  const chartData = rows
    .filter(r => r.numeric_value !== null && !isNaN(r.numeric_value))
    .map(r => ({
      name: r.test_name,
      value: r.numeric_value,
      status: r.status || 'Normal',
      unit: r.unit || ''
    }))

  const getColor = (status) => {
    switch (status) {
      case 'High': return '#EF4444' // Crimson Warning
      case 'Low': return '#3B82F6'  // Blue Info
      default: return '#10B981'     // Emerald Normal
    }
  }

  return (
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 11 }} />
          <YAxis />
          <Tooltip formatter={(val, name, item) => [`${val} ${item.payload.unit}`, `Status: ${item.payload.status}`]} />
          <Bar dataKey="value" radius={[6, 6, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.status)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
```
