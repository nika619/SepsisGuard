import json
import logging
from datetime import datetime
from typing import Optional
from ..services.gemini_client import gemini_client
from ..services.fhir_client import fhir_client
from ..core.data_provider import SyntheticData
from ..utils.helpers import parse_sharp_context, clean_json_response

log = logging.getLogger("sepsisguard.tools.risk")

async def compute_sepsis_risk_tool(
    patient_id: str,
    fhir_context: Optional[str] = None,
    demo_scenario: Optional[str] = None
) -> str:
    """
    Analyzes a patient's clinical data to compute a sepsis risk score (0-100).
    """
    log.info(f"Computing sepsis risk for patient: {patient_id}")

    # 1. Acquire Clinical Context
    clinical_text = ""
    ctx = parse_sharp_context(fhir_context)
    fhir_url = ctx.get("fhirUrl")
    fhir_token = ctx.get("fhirToken")
    pid = ctx.get("patientId") or patient_id

    if fhir_url and pid:
        clinical_text = await fhir_client.fetch_patient_documents(fhir_url, pid, fhir_token)

    if not clinical_text:
        clinical_text = SyntheticData.get_patient(demo_scenario or "high")
        log.info("Using synthetic fallback data")

    # 2. AI Reasoning
    prompt = f"""You are a critical care AI assistant specializing in early sepsis detection.

Analyze the following patient clinical data and compute a sepsis risk score.

CLINICAL DATA:
{clinical_text}

SEPSIS CRITERIA TO CONSIDER:
- qSOFA: altered mentation, RR ≥22, SBP ≤100 (score 0-3)
- SIRS: Temp >38°C or <36°C, HR >90, RR >20, WBC >12k or <4k
- Lactate: ≥2.0 = concern, ≥4.0 = septic shock territory
- Trending vitals (deterioration is a key signal)
- Nursing note language (diaphoretic, confused = red flags)
- Organ dysfunction markers (creatinine, BP, mentation)

Respond ONLY with a valid JSON object in exactly this format, no extra text:
{{
  "patient_id": "{patient_id}",
  "risk_score": <integer 0-100>,
  "risk_level": "<HIGH|MODERATE|LOW>",
  "confidence": "<HIGH|MODERATE|LOW>",
  "reasoning_chain": [
    "<sentence 1: cite specific vital or lab value and what it means>",
    "<sentence 2: cite second specific finding and clinical significance>",
    "<sentence 3: integrate findings and explain overall risk trajectory>"
  ],
  "key_signals": ["<signal 1>", "<signal 2>", "<signal 3>"],
  "patient_summary": "<one sentence clinical summary>",
  "time_sensitivity": "<IMMEDIATE|URGENT|ROUTINE>",
  "assessed_at": "{datetime.utcnow().isoformat()}Z"
}}"""

    raw_response = gemini_client.ask(prompt)
    cleaned_response = clean_json_response(raw_response)

    try:
        # Validate JSON
        json.loads(cleaned_response)
        return cleaned_response
    except json.JSONDecodeError:
        log.error("Gemini returned invalid JSON for risk analysis")
        return json.dumps({
            "error": "Failed to generate structured risk analysis",
            "raw_output": raw_response
        })
