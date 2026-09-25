"""
AI/NLP layer: turns the *structured, validated* extracted results into a
plain-language bilingual (English + Tamil) summary.

Important: the model is given only the structured JSON built by
parser_service + analysis_service - never the raw image - so it cannot
"see" and hallucinate values that OCR didn't actually extract.

The provider is configurable via AI_PROVIDER in the environment
("anthropic" or "openai") so the app isn't locked to one vendor.
"""
import json
from typing import Any, Dict, List, Optional

from app.config import settings

SYSTEM_PROMPT = """You are a medical-report explainer for a patient-facing health app.

You will be given a JSON list of lab test results that were extracted from a
real uploaded report (test name, value, unit, reference range, and a
Normal/Low/High/Unknown status already computed from the report's own
reference range).

Your job is ONLY to explain what is already in that data in plain language.
Rules you must follow strictly:
- Do NOT diagnose any disease or condition.
- Do NOT recommend medicines, dosages, or treatments.
- Do NOT invent test results, values, or reference ranges that are not in the input JSON.
- If a test's status is "Unknown" (no reference range was available), say the
  reference range wasn't provided rather than guessing whether it's normal.
- Keep language simple, calm, and non-alarming.
- The Tamil text should be simple, everyday Tamil (a natural mix of Tamil script
  with common English medical/unit terms left as-is, similar to how Tamil speakers
  actually talk about lab reports) - not stiff formal/literary Tamil, and it must
  NOT mistranslate medical terms.
- CRITICAL FOR LIFESTYLE & PREVENTION: Do NOT give generic one-size-fits-all tips.
  lifestyle_en/ta and prevention_en/ta MUST BE HIGHLY SPECIFIC to the patient's actual
  abnormal or borderline tests:
  * High Blood Sugar / HbA1c: low-GI foods (millets, oats, vegetables), avoid refined sugars/juices, 30-min brisk walk, HbA1c check in 3 months.
  * High Lipids (Cholesterol / Triglycerides / LDL): cut saturated/trans fats and fried items, add omega-3, nuts, soluble fiber, repeat lipid profile in 8-12 weeks.
  * Low Hemoglobin / RBC / Iron: iron-rich foods (moringa leaves, dates, lentils, pomegranate) + vitamin C, avoid tea/coffee with meals, repeat CBC in 6 weeks.
  * High Creatinine / Urea / Uric Acid: kidney hydration (2.5-3L), low salt, avoid OTC painkillers (NSAIDs), repeat renal tests.
  * High Liver enzymes (SGPT / SGOT / Bilirubin): strictly avoid alcohol, minimize oily foods, antioxidant-rich foods, repeat LFT.
  * Thyroid (TSH High/Low): consistent morning medication routine, iodine/selenium balance, 6-8 week recheck.
  * All Normal: praise healthy markers, encourage continuing rainbow diet, regular sleep, and annual preventive checks.

Respond with ONLY a JSON object (no markdown fences, no commentary) with exactly
these keys, all string values:
{
  "overall_summary_en": "...",
  "overall_summary_ta": "...",
  "abnormal_findings_en": "...",
  "abnormal_findings_ta": "...",
  "normal_findings_en": "...",
  "normal_findings_ta": "...",
  "attention_points_en": "...",
  "attention_points_ta": "...",
  "lifestyle_en": "...",
  "lifestyle_ta": "...",
  "prevention_en": "...",
  "prevention_ta": "..."
}

If there are no abnormal findings, abnormal_findings_en/ta should say so briefly.
If there are no normal findings, normal_findings_en/ta should say so briefly.
attention_points should call out anything borderline or worth discussing with a doctor.
lifestyle should provide actionable food & daily habits tailored specifically to the patient's lab markers.
prevention should offer clear clinical monitoring questions and self-care steps for those specific markers.
"""

REQUIRED_KEYS = [
    "overall_summary_en",
    "overall_summary_ta",
    "abnormal_findings_en",
    "abnormal_findings_ta",
    "normal_findings_en",
    "normal_findings_ta",
    "attention_points_en",
    "attention_points_ta",
    "lifestyle_en",
    "lifestyle_ta",
    "prevention_en",
    "prevention_ta",
]


class AIGenerationError(Exception):
    pass


def _build_user_prompt(
    structured_results: List[Dict[str, Any]],
    age: Optional[int],
    gender: Optional[str],
    report_date: Optional[str],
) -> str:
    context = {
        "report_date": report_date,
        "patient_age": age,
        "patient_gender": gender,
        "results": structured_results,
    }
    return (
        "Here is the structured, validated data extracted from the patient's report:\n\n"
        + json.dumps(context, indent=2)
        + "\n\nGenerate the bilingual summary JSON as instructed."
    )


def _extract_json(text: str) -> Dict[str, str]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AIGenerationError(f"AI response was not valid JSON: {exc}") from exc

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise AIGenerationError(f"AI response missing keys: {missing}")
    return {k: str(data[k]) for k in REQUIRED_KEYS}


def _call_anthropic(user_prompt: str) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise AIGenerationError("ANTHROPIC_API_KEY is not set in the environment.")
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _call_openai(user_prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise AIGenerationError("OPENAI_API_KEY is not set in the environment.")
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def _generate_condition_specific_guidance(
    structured_results: List[Dict[str, Any]],
    abnormal: List[Dict[str, Any]],
) -> Dict[str, str]:
    """
    Generates clinically sound, highly tailored food, lifestyle, and
    preventive education based on the exact abnormal lab parameters.
    Never generic; matches specific biomarker deviations in EN + TA.
    """
    en_lifestyle_parts = []
    ta_lifestyle_parts = []
    en_prevention_parts = []
    ta_prevention_parts = []

    # Map abnormal test names to lower case for keyword inspection
    abnormal_names = " ".join([r.get("test_name", "").lower() for r in abnormal])
    
    # 1. Glucose / Diabetes / Glycemic Control
    if any(k in abnormal_names for k in ["glucose", "sugar", "hba1c", "fbs", "ppbs", "rbs"]):
        en_lifestyle_parts.append(
            "• Blood Sugar Focus: Prioritize low-glycemic index, high-fiber foods (whole millets, oats, barley, leafy vegetables, lentils). Strictly limit refined white sugar, sweets, sodas, and white rice. Drink 2.5-3L water daily and maintain a 30-minute brisk walk after meals."
        )
        ta_lifestyle_parts.append(
            "• இரத்த சர்க்கரை வழிகாட்டல்: நார்ச்சத்து மிகுந்த சிறுதானியங்கள், ஓட்ஸ், பச்சை காய்கறிகள் மற்றும் பயறு வகைகளை உணவில் சேர்க்கவும். வெள்ளை சர்க்கரை, இனிப்புகள், குளிர்பானங்கள் மற்றும் வெள்ளை அரிசியைத் தவிர்க்கவும். தினமும் 2.5-3 லிட்டர் தண்ணீர் குடித்து, உணவுக்குப் பின் 30 நிமிடம் நடைபயிற்சி செய்யவும்."
        )
        en_prevention_parts.append(
            "• Glycemic Monitoring: Monitor fasting & post-meal blood sugar weekly. Schedule an HbA1c test every 3 months. Inspect feet daily for cuts or sores, and consult your physician to establish personalized target ranges."
        )
        ta_prevention_parts.append(
            "• சர்க்கரை கண்காணிப்பு: வாரம் ஒருமுறை வெறும் வயிறு மற்றும் உணவுக்குப் பின் சர்க்கரை அளவை பரிசோதிக்கவும். 3 மாதங்களுக்கு ஒருமுறை HbA1c பரிசோதனை செய்து மருத்துவரை அணுகவும்."
        )

    # 2. Lipid Profile / Cholesterol / Cardiovascular Health
    if any(k in abnormal_names for k in ["cholesterol", "triglyceride", "ldl", "vldl", "lipid"]):
        en_lifestyle_parts.append(
            "• Heart & Lipid Wellness: Minimize saturated fats, hydrogenated oils, butter, and deep-fried foods. Add heart-healthy unsaturated fats (walnuts, almonds, flaxseeds, olive oil) and soluble fiber (oats, beans). Engage in 40 minutes of aerobic exercise 4-5 days weekly."
        )
        ta_lifestyle_parts.append(
            "• கொழுப்பு & இதய பாதுகாப்பு: நெய், எண்ணெய் பதார்த்தங்கள், துரித உணவுகள் மற்றும் வறுத்த உணவுகளைக் குறைக்கவும். பாதாம், வால்நட் மற்றும் ஓட்ஸ் போன்ற நார்ச்சத்து உணவுகளைச் சேர்க்கவும். வாரத்தில் 4-5 நாட்கள் உடற்பயிற்சி செய்யவும்."
        )
        en_prevention_parts.append(
            "• Cardiovascular Check: Repeat complete Lipid Profile test after 8-12 weeks of dietary intervention. Monitor blood pressure periodically and review cardiovascular risk profile with your doctor."
        )
        ta_prevention_parts.append(
            "• இதய பராமரிப்பு: 2-3 மாதங்களில் மீண்டும் Lipid Profile பரிசோதனை செய்யவும். ரத்த அழுத்தத்தை (BP) சீராக சரிபார்த்து மருத்துவ ஆலோசனை பெறவும்."
        )

    # 3. Anemia / Hemoglobin / RBC / Iron Deficiency
    if any(k in abnormal_names for k in ["hemoglobin", "hb", "rbc", "iron", "ferritin", "hematocrit", "pcv"]):
        en_lifestyle_parts.append(
            "• Iron & Hemoglobin Nutrition: Consume iron-dense foods such as drumstick/moringa leaves (முருங்கைக்கீரை), beetroot, dates, raisins, pomegranate, lentils, and lean meat. Pair with Vitamin C (lemon, amla) to maximize iron absorption. Avoid tea or coffee within 1 hour of meals."
        )
        ta_lifestyle_parts.append(
            "• ஹீமோகுளோபின் வழிகாட்டல்: முருங்கைக்கீரை, பீட்ரூட், பேரீச்சம்பழம், உலர் திராட்சை, மாதுளை, நெல்லிக்காய் மற்றும் பருப்பு வகைகளை அதிகம் சாப்பிடவும். இரும்புச்சத்து உறிஞ்சப்பட எலுமிச்சை/நெல்லிக்காய் நல்லது. சாப்பிட்டவுடன் டீ/காபி குடிப்பதைத் தவிர்க்கவும்."
        )
        en_prevention_parts.append(
            "• Anemia Tracking: Recheck Complete Blood Count (CBC) and serum ferritin in 6-8 weeks. If experiencing persistent fatigue, dizziness, or shortness of breath, consult your physician for clinical iron supplementation."
        )
        ta_prevention_parts.append(
            "• இரத்த சோகை கண்காணிப்பு: 6-8 வாரங்களில் மீண்டும் CBC பரிசோதனை செய்யவும். தலைசுற்றல் அல்லது அதிக சோர்வு இருந்தால் மருத்துவரிடம் காண்பித்து ஆலோசனை பெறவும்."
        )

    # 4. Kidney Function / Creatinine / Urea / Uric Acid
    if any(k in abnormal_names for k in ["creatinine", "urea", "bun", "uric acid"]):
        en_lifestyle_parts.append(
            "• Renal & Kidney Care: Maintain adequate daily hydration (2.5-3 liters unless medically restricted). Reduce dietary sodium/salt, processed meats, purine-rich foods, and unmonitored high-protein supplements."
        )
        ta_lifestyle_parts.append(
            "• சிறுநீரக பாதுகாப்பு: மருத்துவர் பரிந்துரைத்த அளவு போதிய தண்ணீர் (2.5-3 லிட்டர்) குடிக்கவும். அதிக உப்பு, பதப்படுத்தப்பட்ட உணவுகள் மற்றும் அசைவ உணவுகளைக் குறைக்கவும்."
        )
        en_prevention_parts.append(
            "• Renal Monitoring: Strictly avoid self-administering over-the-counter pain medications (NSAIDs like ibuprofen) which can place stress on kidneys. Schedule a repeat Kidney Function Test (KFT) in 4-6 weeks under physician guidance."
        )
        ta_prevention_parts.append(
            "• சிறுநீரக பராமரிப்பு: மருத்துவர் அனுமதியின்றி வலி மாத்திரைகள் (painkillers) எடுப்பதைத் தவிர்க்கவும். 1 மாதத்தில் மீண்டும் சிறுநீரக பரிசோதனை (RFT) செய்து மருத்துவரை அணுகவும்."
        )

    # 5. Liver Function / SGPT / SGOT / Bilirubin / ALP
    if any(k in abnormal_names for k in ["sgpt", "alt", "sgot", "ast", "bilirubin", "alkaline phosphatase", "alp", "ggt"]):
        en_lifestyle_parts.append(
            "• Liver Protection: Strictly avoid all alcohol consumption. Limit heavily fried, greasy, and processed foods. Emphasize antioxidant-rich foods (papaya, cruciferous greens, turmeric, green tea) and stay well-hydrated."
        )
        ta_lifestyle_parts.append(
            "• கல்லீரல் வழிகாட்டல்: மது அருந்துவதை முற்றிலும் தவிர்க்கவும். அதிக எண்ணெய், கொழுப்பு உணவுகளைத் தவிர்க்கவும். மஞ்சள், பப்பாளி, கீரைகள் மற்றும் பழங்களை உணவில் சேர்க்கவும்."
        )
        en_prevention_parts.append(
            "• Hepatic Follow-up: Avoid unnecessary hepatotoxic medications or supplements. Schedule a follow-up Liver Function Test (LFT) and physician consultation within 4 weeks."
        )
        ta_prevention_parts.append(
            "• கல்லீரல் கண்காணிப்பு: தேவையற்ற மாத்திரைகளைத் தவிர்க்கவும். 4 வாரங்களில் மீண்டும் LFT பரிசோதனை செய்து மருத்துவரிடம் ஆலோசனை பெறவும்."
        )

    # 6. Thyroid Profile (TSH, T3, T4)
    if any(k in abnormal_names for k in ["tsh", "t3", "t4", "thyroid"]):
        en_lifestyle_parts.append(
            "• Thyroid Metabolic Balance: Ensure balanced dietary intake of iodine and selenium (eggs, whole grains, nuts). Limit excessive consumption of raw cruciferous vegetables if hypothyroid. Maintain steady sleep and stress management."
        )
        ta_lifestyle_parts.append(
            "• தைராய்டு வழிகாட்டல்: சமச்சீரான சத்துக்கள் நிறைந்த உணவுகள், முட்டை மற்றும் நட்ஸ் வகைகளை உட்கொள்ளவும். சீரான தூக்கத்தை பராமரிக்கவும்."
        )
        en_prevention_parts.append(
            "• Thyroid Monitoring: If prescribed thyroid medication, take it consistently first thing in the morning on an empty stomach with plain water. Recheck serum TSH after 6-8 weeks."
        )
        ta_prevention_parts.append(
            "• தைராய்டு பராமரிப்பு: தைராய்டு மாத்திரை பரிந்துரைக்கப்பட்டால், காலையில் வெறும் வயிற்றில் தவறாமல் எடுக்கவும். 6-8 வாரங்களில் மீண்டும் TSH பரிசோதனை செய்யவும்."
        )

    # 7. Vitamins & Minerals (Vitamin D, B12, Calcium)
    if any(k in abnormal_names for k in ["vitamin d", "vit d", "vitamin b12", "vit b12", "calcium"]):
        en_lifestyle_parts.append(
            "• Vitamin & Mineral Replenishment: For Vitamin D, obtain 15-20 minutes of mild early-morning sun exposure and consume fortified milk or egg yolks. For B12, consume dairy products, eggs, or fortified foods."
        )
        ta_lifestyle_parts.append(
            "• வைட்டமின் ஊட்டச்சத்து: காலையில் 15-20 நிமிடங்கள் மிதமான வெயிலில் இருக்கவும். பால், முட்டை மற்றும் ஊட்டச்சத்து நிறைந்த உணவுகளை உட்கொள்ளவும்."
        )
        en_prevention_parts.append(
            "• Vitamin Follow-up: Review clinical supplementation (e.g. weekly Vitamin D3 or daily B12) with your doctor and retest serum levels in 3 months."
        )
        ta_prevention_parts.append(
            "• வைட்டமின் கண்காணிப்பு: மருத்துவர் ஆலோசனையுடன் தேவையான வைட்டமின் மாத்திரைகளை எடுத்துக்கொண்டு 3 மாதங்களில் மீண்டும் பரிசோதிக்கவும்."
        )

    # 8. Platelets / Infection / WBC
    if any(k in abnormal_names for k in ["platelet", "wbc", "leukocyte"]):
        en_lifestyle_parts.append(
            "• Immunity & Platelet Support: Emphasize immune-boosting fruits (papaya, kiwi, citrus, pomegranate) and stay hydrated. Avoid activities with high risk of injury, cuts, or bleeding."
        )
        ta_lifestyle_parts.append(
            "• பிளேட்லெட் & நோய் எதிர்ப்பு: பப்பாளி, மாதுளை, சிட்ரஸ் பழங்கள் மற்றும் சத்தான உணவுகளை உட்கொள்ளவும். காயங்கள் அல்லது ரத்தக்கசிவு ஏற்படாமல் கவனமாக இருக்கவும்."
        )
        en_prevention_parts.append(
            "• Platelet Vigilance: Immediately seek medical attention if you notice unexplained bruising, bleeding gums, or fever. Recheck CBC within 48-72 hours if acute."
        )
        ta_prevention_parts.append(
            "• பிளேட்லெட் கண்காணிப்பு: பல் ஈறுகளில் ரத்தம், உடலில் தடிப்புகள் அல்லது காய்ச்சல் இருந்தால் உடனே மருத்துவரை அணுகவும்."
        )

    # If all normal or no specific abnormal matches found, give healthy maintenance guidance
    if not en_lifestyle_parts:
        en_lifestyle_parts.append(
            "• Balanced Health Maintenance: All tested values are within healthy limits! Maintain this excellent baseline with a colorful rainbow diet rich in vegetables, whole grains, and lean proteins. Drink 2.5L water daily and engage in 150 minutes of weekly moderate exercise."
        )
        ta_lifestyle_parts.append(
            "• சமச்சீர் ஆரோக்கிய வழிகாட்டல்: பரிசோதிக்கப்பட்ட அனைத்து அளவீடுகளும் இயல்பாக உள்ளன! காய்கறிகள், கீரைகள் மற்றும் முழு தானியங்கள் நிறைந்த சமச்சீர் உணவை தொடரவும். தினமும் 2.5 லிட்டர் தண்ணீர் குடித்து உடற்பயிற்சி செய்து உடலை நற்பேணுங்கள்."
        )
        en_prevention_parts.append(
            "• Preventive Wellness: Continue annual wellness health screenings, prioritize 7-8 hours of sound sleep, manage stress through regular walking or meditation, and maintain copies of your reports."
        )
        ta_prevention_parts.append(
            "• வருமுன் காப்போம்: ஆண்டுதோறும் வழக்கமான முழு உடல் பரிசோதனை செய்து கொள்ளவும். தினமும் 7-8 மணிநேரம் தூங்கி, மன அமைதியை பேணி ஆரோக்கியமாக வாழுங்கள்."
        )

    return {
        "lifestyle_en": "\n\n".join(en_lifestyle_parts),
        "lifestyle_ta": "\n\n".join(ta_lifestyle_parts),
        "prevention_en": "\n\n".join(en_prevention_parts),
        "prevention_ta": "\n\n".join(ta_prevention_parts),
    }


def _generate_fallback_summary(structured_results: List[Dict[str, Any]]) -> Dict[str, str]:
    abnormal = [r for r in structured_results if r.get("status") in ("Low", "High")]
    normal = [r for r in structured_results if r.get("status") == "Normal"]

    abnormal_en_list = [
        f"{r['test_name']}: {r['value']} {r.get('unit','')}".strip() + f" ({r['status']})"
        for r in abnormal
    ]
    abnormal_ta_list = [
        f"{r['test_name']}: {r['value']} {r.get('unit','')}".strip()
        + f" ({'அதிகம்' if r['status']=='High' else 'குறைவு'})"
        for r in abnormal
    ]

    normal_en_list = [
        f"{r['test_name']}: {r['value']} {r.get('unit','')}".strip() for r in normal
    ]
    normal_ta_list = [
        f"{r['test_name']}: {r['value']} {r.get('unit','')}".strip() for r in normal
    ]

    guidance = _generate_condition_specific_guidance(structured_results, abnormal)

    return {
        "overall_summary_en": (
            f"Analysis complete for {len(structured_results)} test parameter(s). "
            f"Found {len(abnormal)} abnormal value(s) and {len(normal)} normal value(s)."
        ),
        "overall_summary_ta": (
            f"மொத்தம் {len(structured_results)} பரிசோதனை அளவீடுகள் ஆய்வு செய்யப்பட்டன. "
            f"{len(abnormal)} அளவீடுகள் மாறுபட்டுள்ளன, {len(normal)} அளவீடுகள் இயல்பாக உள்ளன."
        ),
        "abnormal_findings_en": (
            ", ".join(abnormal_en_list)
            if abnormal_en_list
            else "All test parameters are within their normal reference ranges."
        ),
        "abnormal_findings_ta": (
            ", ".join(abnormal_ta_list)
            if abnormal_ta_list
            else "அனைத்து பரிசோதனை முடிவுகளும் இயல்பு எல்லையில் உள்ளன."
        ),
        "normal_findings_en": (
            ", ".join(normal_en_list)
            if normal_en_list
            else "No parameters in normal range."
        ),
        "normal_findings_ta": (
            ", ".join(normal_ta_list)
            if normal_ta_list
            else "இயல்பு எல்லையில் பதிவு செய்யப்பட்ட அளவீடுகள் இல்லை."
        ),
        "attention_points_en": (
            f"Please review abnormal findings ({', '.join(r['test_name'] for r in abnormal)}) with a registered medical doctor for clinical interpretation."
            if abnormal
            else "Maintain regular health checkups and consult your physician for clinical interpretation."
        ),
        "attention_points_ta": (
            f"மாறுபட்ட அளவீடுகளை ({', '.join(r['test_name'] for r in abnormal)}) உங்கள் மருத்துவரிடம் காண்பித்து ஆலோசனை பெறவும்."
            if abnormal
            else "வழக்கமான மருத்துவ பரிசோதனைகளை மேற்கொண்டு உங்கள் மருத்துவரிடம் ஆலோசனை பெறவும்."
        ),
        "lifestyle_en": guidance["lifestyle_en"],
        "lifestyle_ta": guidance["lifestyle_ta"],
        "prevention_en": guidance["prevention_en"],
        "prevention_ta": guidance["prevention_ta"],
        "ai_provider": "rule_engine_fallback",
        "ai_model": "clinical-rules-v2",
    }



def generate_bilingual_summary(
    structured_results: List[Dict[str, Any]],
    age: Optional[int] = None,
    gender: Optional[str] = None,
    report_date: Optional[str] = None,
) -> Dict[str, str]:
    if not structured_results:
        raise AIGenerationError(
            "No structured test results were available to summarize. "
            "Correct/add rows before generating a summary."
        )

    user_prompt = _build_user_prompt(structured_results, age, gender, report_date)

    provider = settings.AI_PROVIDER.lower()
    try:
        if provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            raw = _call_anthropic(user_prompt)
            result = _extract_json(raw)
            result["ai_provider"] = provider
            result["ai_model"] = settings.ANTHROPIC_MODEL
            return result
        elif provider == "openai" and settings.OPENAI_API_KEY:
            raw = _call_openai(user_prompt)
            result = _extract_json(raw)
            result["ai_provider"] = provider
            result["ai_model"] = settings.OPENAI_MODEL
            return result
        else:
            return _generate_fallback_summary(structured_results)
    except Exception as exc:
        print(f"AI generation warning: {exc}. Using fallback summary generator.")
        return _generate_fallback_summary(structured_results)

