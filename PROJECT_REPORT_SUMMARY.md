# PROJECT REPORT: MedReport AI
**An Intelligent Bilingual Medical Lab Report Extraction, Clinical Decision Support, and Patient Health Education System**

---

## 1. ABSTRACT
Medical laboratory reports are laden with complex technical jargon, clinical terminology, and numerical reference ranges that are often incomprehensible to non-medical individuals. This information asymmetry leads to patient anxiety, delayed consultations, or misinterpretation of lab findings. 

**MedReport AI** is an end-to-end healthcare web platform designed to bridge this communication gap. The system enables users to upload diagnostic laboratory reports in image (JPG/PNG) or document (PDF) formats. Utilizing **Tesseract Optical Character Recognition (OCR) powered by LSTM Deep Neural Networks**, unstructured medical records are digitized. A **Rule-based Heuristic NLP Parser** extracts clinical parameters, units, values, and biological reference ranges. A **Clinical Decision Support System (CDSS)** evaluates each biomarker against biological thresholds to categorize values as Normal, High, or Low without diagnostic hallucination. Finally, a **Medical NLP & Generative AI Layer** synthesizes plain-language, bilingual (English & Tamil) educational summaries, disease risk factors, tailored nutritional advice, and preventive self-care guidelines. MedReport AI offers both instant Guest Analysis and an authenticated user tracking portal, prioritizing patient safety, data integrity, and linguistic inclusivity.

---

## 2. PROBLEM STATEMENT & MOTIVATION
1. **Complicated Terminology:** Diagnostic reports contain medical shorthand and biochemical indices (e.g., HbA1c, eGFR, SGPT/ALT, TSH) that average patients cannot easily understand.
2. **Language Barrier:** In multilingual regions like Tamil Nadu, lab reports are provided exclusively in English, leaving vernacular-speaking patients dependent on third-party translation.
3. **Medical Safety Concerns:** Generic AI models often hallucinate fake medical findings or attempt to prescribe prescription medications without human clinical oversight.
4. **Lack of Actionable Education:** Patients often receive numbers without knowing what diet (e.g., glycemic control vs. low purine vs. iron-rich) or lifestyle steps they should adopt prior to seeing their physician.

---

## 3. PROJECT OBJECTIVES
* **Automated Document Ingestion:** Read and digitize medical lab reports from varied formats (PDFs and smartphone photos).
* **Deterministic Information Extraction:** Extract Test Name, Result Value, Unit, and Reference Range without AI hallucination.
* **Biomarker Risk Stratification:** Compare numerical values against reference ranges to flag abnormal health markers across 7 major clinical categories.
* **Bilingual Patient Education:** Generate non-alarmist, plain-language explanations in English and everyday conversational Tamil.
* **Targeted Health Guidance:** Provide evidence-based food, lifestyle, and preventive monitoring tips specific to each patient's actual biomarker deviations.
* **Clinical Safety by Design:** Maintain an explicit non-diagnostic, non-prescriptive posture, guiding patients to certified medical professionals.

---

## 4. SYSTEM ARCHITECTURE & PIPELINE

```
+-----------------------------------------------------------------------+
|                         MedReport AI Pipeline                         |
+-----------------------------------------------------------------------+

  [ User Upload: Lab Report Image / PDF ]
                     |
                     v
  [ Layer 1: Computer Vision & Preprocessing ]
    * PyMuPDF (300 DPI PDF Rendering)
    * Pillow (Grayscale & Contrast Enhancement)
    * Tesseract OCR Engine (LSTM Neural Network, PSM 6, OEM 3)
                     |
                     v
  [ Layer 2: Heuristic NLP Parsing & Data Structuring ]
    * Regular Expression Tokenization (LINE_SPLIT_RE, VALUE_RE, RANGE_RE)
    * Value Anchor Detection & Noise Filtering
    * Extraction into Structured JSON Model
                     |
                     v
  [ Layer 3: Clinical Decision Support System (CDSS) ]
    * Deterministic Multi-Threshold Boundary Evaluation
    * Status Classification: Normal | Low | High | Unknown
    * Parameter Corrections & User Overrides
                     |
                     v
  [ Layer 4: Medical NLP & Bilingual Advisory Engine ]
    * Generative AI (Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o)
    * Deterministic Clinical Rule Engine Fallback (Zero-API dependency)
    * Biomarker-Specific Lifestyle & Preventive Care Mapping (EN + TA)
                     |
                     v
  [ Layer 5: Interactive Web Presentation Layer ]
    * React 18 + Vite SPA (White, Lavender, & Purple Healthcare Theme)
    * Interactive Data Visualizations (Recharts Bar & Range Comparative Charts)
    * Guest Quick Analysis + Registered User Report History Portal
```

---

## 5. TECHNICAL STACK & SPECIFICATIONS

### Frontend Technology
* **Framework:** React.js (v18.3.1) with Modern Functional Components & Hooks
* **Routing:** React Router DOM (v6.26.2) with Client-side SPA navigation
* **Build System:** Vite (v5.4.6) for lightning-fast HMR and bundling
* **Visualizations:** Recharts (v2.12.7) for patient biomarker reference range charts
* **HTTP Client:** Axios (v1.7.7) with unified error handling and proxy integration
* **Styling:** Custom Vanilla CSS3 Design System (Clean White, Soft Lavender `#F3E8FF`, Primary Purple `#7C3AED`)

### Backend Technology
* **Web Framework:** FastAPI (v0.115.0) — High-performance asynchronous REST API
* **ASGI Server:** Uvicorn (v0.30.6) with hot-reload
* **Database & ORM:** SQLAlchemy (v2.0.35) with SQLite (local fallback) and MySQL / PyMySQL (v1.1.1) support
* **Data Validation:** Pydantic (v2.9.2) & Pydantic-Settings
* **Computer Vision / OCR:** Tesseract OCR (v5.0) via `pytesseract` (v0.3.13)
* **Document Processing:** PyMuPDF (`fitz` v1.24.10) & Pillow (`PIL` v10.4.0)
* **AI / LLM Integration:** Anthropic Claude SDK (v0.34.2) & OpenAI SDK (v1.51.0) with rule-based failover

---

## 6. DATASET & CLINICAL BENCHMARKS

The project incorporates two dataset structures:
1. **Dynamic Extracted Dataset:** Real-time user uploads stored across 4 normalized relational database tables:
   * `users` — Patient metadata, authentication records.
   * `reports` — Upload records, original files, status tracking, timestamps.
   * `extracted_results` — Atomic test parameters (test name, value, unit, reference range, status).
   * `analysis_results` — Bilingual explanations, lifestyle guidance, and preventive advice.

2. **Kaggle Benchmark Dataset (`kaggle_medical_lab_dataset.csv`):**
   * 31 detailed biomarker records spanning 7 clinical profiles:
     - **Diabetes:** Fasting Blood Sugar, HbA1c
     - **Cardiovascular / Lipids:** Total Cholesterol, Triglycerides, HDL, LDL
     - **Hematology (CBC):** Hemoglobin, RBC Count, Platelets, WBC Count
     - **Renal / Kidney:** Serum Creatinine, Blood Urea, Uric Acid
     - **Hepatic / Liver:** SGPT (ALT), SGOT (AST), Bilirubin, Alkaline Phosphatase
     - **Endocrine:** TSH, Total T3, Total T4
     - **Vitamins & Minerals:** Serum Ferritin, Vitamin D (25-OH), Vitamin B12

---

## 7. KEY MODULES & FEATURES

1. **Dual User Experience (Guest Mode & Registered User):**
   * *Quick Analysis / Guest Mode:* Zero friction; patients upload and view analyses immediately without registration.
   * *User Accounts:* Secure sign-up/sign-in enabling persistent medical report history and chronological lab tracking.

2. **Optical Character Recognition (OCR) Engine:**
   * Automatically handles scanned lab sheets and multi-page PDFs using 300 DPI rasterization and grayscale enhancement.

3. **Interactive OCR Review & Correction Table:**
   * Allows patients to verify and manually correct any misread OCR text before final analysis to guarantee 100% accuracy.

4. **Multi-Category Biomarker Charting:**
   * Interactive bar charts visually highlighting where a patient's numerical result falls relative to the safe reference bracket.

5. **Bilingual AI Summaries (English & Tamil):**
   * Clear breakdowns into: Overall Summary, Abnormal Findings, Normal Findings, and Doctor Discussion Points.

6. **Condition-Specific Lifestyle & Preventive Care Advice:**
   * Targeted food recommendations (e.g., moringa/dates for anemia, millets/oats for diabetes, zero alcohol for elevated liver enzymes).
   * Targeted preventive checks (e.g., 3-month HbA1c, 6-week CBC, avoiding OTC NSAIDs for kidney strain).

---

## 8. CLINICAL SAFETY & ETHICAL COMPLIANCE
* **No Disease Hallucination:** If a reference range is absent from the report, the system marks the status as `"Unknown"` rather than guessing.
* **Strict Non-Prescription Policy:** The system under no circumstances prescribes prescription drugs, dosages, or self-treatment regimens.
* **Persistent Medical Disclaimer:** Every page explicitly reminds users that MedReport AI is an informational tool and does not replace a registered medical practitioner.

---

## 9. CONCLUSION & FUTURE SCOPE
MedReport AI modernizes health literacy by demystifying complex lab reports and delivering accessible, vernacular health education to patients.

**Future Enhancements:**
* Expanding multilingual support to Hindi, Telugu, and Malayalam.
* Longitudinal trend charts tracking patient biomarkers over 6 to 12 months.
* Direct FHIR / HL7 clinical interoperability with hospital electronic health records (EHR).
* Mobile application deployment using React Native / Flutter.
