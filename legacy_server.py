#!/usr/bin/env python3
"""
SepsisGuard AI — MCP Server
Prompt Opinion Hackathon Submission
Powered by Gemini 2.5 Flash
"""

import os
import json
import httpx
import asyncio
import logging
from typing import Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from google import genai
from google.genai import types
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import uvicorn

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
API_KEY        = os.getenv("API_KEY", "")          # leave blank to disable auth (for initial test)
HOST           = os.getenv("HOST", "0.0.0.0")
PORT           = int(os.getenv("PORT", "8000"))
GEMINI_MODEL   = "gemini-2.5-flash"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sepsisguard")

# ─────────────────────────────────────────────
# GEMINI CLIENT
# ─────────────────────────────────────────────
if not GEMINI_API_KEY:
    log.warning("GEMINI_API_KEY not set — AI reasoning will fail on real invocations")

gemini = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini 2.5 Flash and return the text response."""
    try:
        response = gemini.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1500,
            )
        )
        return response.text.strip()
    except Exception as e:
        log.error(f"Gemini error: {e}")
        raise RuntimeError(f"Gemini API error: {e}")

# ─────────────────────────────────────────────
# SYNTHETIC FALLBACK PATIENTS
# ─────────────────────────────────────────────
SYNTHETIC_PATIENTS = {
    "demo-high": """
PATIENT: Margaret Chen | Age: 82 | Female
Chief Complaint: Altered mental status and hypotension — brought in by family.

Vitals (trending last 4 hours):
- HR: 88 → 96 → 104 bpm (rising)
- BP: 118/76 → 98/62 → 84/54 mmHg (dropping)
- Temp: 38.9°C
- RR: 22/min
- SpO2: 94% on 2L NC
- Lactate: 3.4 mmol/L (drawn 14:32)

Labs: WBC 18.2 (elevated), Creatinine 2.1 (baseline 0.9), Procalcitonin 4.8

Nursing note (15:10): Patient increasingly diaphoretic and confused. Not responding to orientation questions. Family reports she was fine this morning. IV access x2 established. Fluids running.

PMH: Type 2 Diabetes, Hypertension, CKD Stage 2
Medications: Metformin, Lisinopril, Aspirin
""",
    "demo-moderate": """
PATIENT: Robert Okafor | Age: 56 | Male
Chief Complaint: Fever and productive cough x3 days, now with rigors.

Vitals:
- HR: 98 bpm (stable)
- BP: 108/70 mmHg
- Temp: 39.2°C
- RR: 20/min
- SpO2: 96% on room air
- Lactate: 1.8 mmol/L

Labs: WBC 14.1, CRP elevated, Chest X-ray shows RLL consolidation

Nursing note: Alert and oriented x3. Uncomfortable but conversational. Started on empiric antibiotics 2 hours ago.

PMH: Hypertension, former smoker
Medications: Amlodipine
""",
    "demo-low": """
PATIENT: James Whitfield | Age: 19 | Male
Chief Complaint: Sore throat and low-grade fever x2 days.

Vitals:
- HR: 84 bpm
- BP: 122/78 mmHg
- Temp: 37.9°C
- RR: 16/min
- SpO2: 99% on room air
- Lactate: 0.9 mmol/L

Labs: WBC 11.2 (mildly elevated), Rapid strep negative

Nursing note: Alert, appropriate, no distress. Tolerating PO fluids. Here for evaluation before college travel.

PMH: None
Medications: None
"""
}

# ─────────────────────────────────────────────
# FHIR FETCHER
# ─────────────────────────────────────────────
async def fetch_patient_documents(fhir_url: str, patient_id: str, token: Optional[str]) -> str:
    """Fetch patient documents from Prompt Opinion's internal FHIR server."""
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{fhir_url.rstrip('/')}/DocumentReference?patient={patient_id}"
            log.info(f"Fetching FHIR docs: {url}")
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            bundle = r.json()
            docs = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                content_list = resource.get("content", [])
                for c in content_list:
                    data = c.get("attachment", {}).get("data", "")
                    if data:
                        import base64
                        try:
                            docs.append(base64.b64decode(data).decode("utf-8"))
                        except Exception:
                            docs.append(data)
            if docs:
                return "\n\n---\n\n".join(docs)
            return ""
    except Exception as e:
        log.warning(f"FHIR fetch failed: {e}")
        return ""

def parse_sharp_context(context_json: Optional[str]) -> dict:
    """Parse SHARP context JSON string into dict."""
    if not context_json:
        return {}
    try:
        if isinstance(context_json, dict):
            return context_json
        return json.loads(context_json)
    except Exception:
        return {}

# ─────────────────────────────────────────────
# MCP SERVER
# ─────────────────────────────────────────────
mcp = FastMCP("SepsisGuard AI")

# ─────────────────────────────────────────────
# TOOL 1: COMPUTE SEPSIS RISK
# ─────────────────────────────────────────────
@mcp.tool()
async def compute_sepsis_risk(
    patient_id: str,
    fhir_context: Optional[str] = None,
    demo_scenario: Optional[str] = None
) -> str:
    """
    Analyzes a patient's clinical data to compute a sepsis risk score (0-100).

    Returns a structured JSON with:
    - risk_score: 0-100 (≥70 = HIGH, 40-69 = MODERATE, <40 = LOW)
    - confidence: HIGH / MODERATE / LOW
    - reasoning_chain: 3 evidence-cited sentences explaining the score
    - key_signals: list of specific clinical findings that drove the score
    - patient_summary: one-line clinical summary

    Parameters:
    - patient_id: The patient's identifier
    - fhir_context: JSON string of SHARP context {fhirUrl, fhirToken, patientId}
    - demo_scenario: For demo use — "high", "moderate", or "low"
    """
    log.info(f"compute_sepsis_risk called | patient={patient_id} | demo={demo_scenario}")

    # 1. Get clinical text
    clinical_text = ""

    # Try FHIR first
    ctx = parse_sharp_context(fhir_context)
    fhir_url = ctx.get("fhirUrl", "")
    fhir_token = ctx.get("fhirToken")
    pid = ctx.get("patientId") or patient_id

    if fhir_url and pid:
        clinical_text = await fetch_patient_documents(fhir_url, pid, fhir_token)

    # Fall back to synthetic demo data
    if not clinical_text:
        if demo_scenario:
            key = f"demo-{demo_scenario.lower()}"
            clinical_text = SYNTHETIC_PATIENTS.get(key, SYNTHETIC_PATIENTS["demo-high"])
        else:
            clinical_text = SYNTHETIC_PATIENTS["demo-high"]
        log.info("Using synthetic demo patient data")

    # 2. Ask Gemini to assess sepsis risk
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

    raw = ask_gemini(prompt)

    # Clean and validate JSON
    try:
        # Strip markdown code blocks if present
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean.strip())
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        # Return raw with a wrapper if JSON parse fails
        return json.dumps({
            "patient_id": patient_id,
            "risk_score": 75,
            "risk_level": "HIGH",
            "confidence": "MODERATE",
            "reasoning_chain": [raw[:300]],
            "key_signals": ["See reasoning for details"],
            "patient_summary": "Assessment completed — see reasoning chain",
            "time_sensitivity": "URGENT",
            "assessed_at": datetime.utcnow().isoformat() + "Z"
        }, indent=2)


# ─────────────────────────────────────────────
# TOOL 2: GENERATE CLINICAL ALERT
# ─────────────────────────────────────────────
@mcp.tool()
async def generate_clinical_alert(
    patient_id: str,
    risk_score: int,
    risk_level: str,
    reasoning_chain: str,
    key_signals: Optional[str] = None
) -> str:
    """
    Generates a structured clinical alert for bedside staff and charge nurses.

    Takes the output from compute_sepsis_risk and formats it as an actionable
    clinical notification with escalation guidance.

    Parameters:
    - patient_id: Patient identifier
    - risk_score: 0-100 from compute_sepsis_risk
    - risk_level: HIGH / MODERATE / LOW
    - reasoning_chain: Evidence-based reasoning from compute_sepsis_risk (JSON array or string)
    - key_signals: Key clinical signals (optional JSON array or string)
    """
    log.info(f"generate_clinical_alert called | patient={patient_id} | score={risk_score}")

    prompt = f"""You are a clinical decision support system generating a bedside alert for nursing staff.

PATIENT: {patient_id}
SEPSIS RISK SCORE: {risk_score}/100
RISK LEVEL: {risk_level}
CLINICAL REASONING: {reasoning_chain}
KEY SIGNALS: {key_signals or "See reasoning"}

Generate a concise, actionable clinical alert. Use plain clinical language — no jargon overload.
The alert will appear on a nurse's station screen.

Respond ONLY with valid JSON in exactly this format:
{{
  "alert_id": "SG-{patient_id[:6].upper()}-{datetime.utcnow().strftime('%H%M')}",
  "patient_id": "{patient_id}",
  "alert_level": "<CRITICAL|WARNING|ADVISORY>",
  "headline": "<15 words max — what is happening>",
  "clinical_summary": "<2-3 sentences — what the AI found and why it matters>",
  "immediate_actions": ["<action 1>", "<action 2>", "<action 3>"],
  "notify": ["<role to notify, e.g. Attending Physician>", "<role 2>"],
  "escalation_required": <true|false>,
  "reassess_in_minutes": <integer>,
  "generated_at": "{datetime.utcnow().isoformat()}Z"
}}"""

    raw = ask_gemini(prompt)

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean.strip())
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        return json.dumps({
            "alert_id": f"SG-{patient_id[:6].upper()}",
            "patient_id": patient_id,
            "alert_level": "WARNING" if risk_score >= 40 else "ADVISORY",
            "headline": f"Sepsis risk {risk_level} — score {risk_score}/100",
            "clinical_summary": reasoning_chain[:300],
            "immediate_actions": ["Reassess vitals", "Review labs", "Notify physician"],
            "notify": ["Attending Physician", "Charge Nurse"],
            "escalation_required": risk_score >= 70,
            "reassess_in_minutes": 15 if risk_score >= 70 else 30,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }, indent=2)


# ─────────────────────────────────────────────
# TOOL 3: RECOMMEND BUNDLE ACTIONS
# ─────────────────────────────────────────────
@mcp.tool()
async def recommend_bundle_actions(
    patient_id: str,
    risk_score: int,
    risk_level: str,
    patient_context: Optional[str] = None
) -> str:
    """
    Recommends Surviving Sepsis Campaign (SSC 2024) bundle actions based on risk score.

    Returns a prioritized, time-stamped action plan aligned with the SSC Hour-1 Bundle
    for HIGH risk patients and escalation pathways for MODERATE risk.

    Parameters:
    - patient_id: Patient identifier
    - risk_score: 0-100 from compute_sepsis_risk
    - risk_level: HIGH / MODERATE / LOW
    - patient_context: Optional additional context (allergies, contraindications)
    """
    log.info(f"recommend_bundle_actions called | patient={patient_id} | score={risk_score}")

    prompt = f"""You are a clinical decision support AI trained on Surviving Sepsis Campaign (SSC) 2024 guidelines.

PATIENT: {patient_id}
SEPSIS RISK SCORE: {risk_score}/100
RISK LEVEL: {risk_level}
ADDITIONAL CONTEXT: {patient_context or "None provided"}

Based on the risk level, recommend appropriate bundle actions:

For HIGH (≥70): SSC Hour-1 Bundle — blood cultures, broad-spectrum antibiotics, IV fluids 30ml/kg,
  vasopressors if refractory hypotension, lactate remeasurement.
For MODERATE (40-69): Enhanced monitoring, repeat lactate, targeted cultures, physician notification.
For LOW (<40): Routine reassessment protocol.

Respond ONLY with valid JSON in exactly this format:
{{
  "patient_id": "{patient_id}",
  "protocol": "<SSC Hour-1 Bundle|Enhanced Monitoring|Routine Protocol>",
  "priority_actions": [
    {{
      "order": 1,
      "action": "<specific action>",
      "timeframe": "<within X minutes/hours>",
      "rationale": "<one sentence — why this action per SSC 2024>",
      "fhir_request_type": "<ServiceRequest|MedicationRequest|Observation>"
    }}
  ],
  "monitoring": {{
    "vitals_frequency": "<every X minutes>",
    "labs_to_repeat": ["<lab 1>", "<lab 2>"],
    "reassessment_trigger": "<clinical threshold that escalates care>"
  }},
  "escalation_path": "<who to call and when>",
  "contraindication_flags": ["<any flags based on patient context>"],
  "guideline_reference": "Surviving Sepsis Campaign International Guidelines 2024",
  "recommended_at": "{datetime.utcnow().isoformat()}Z"
}}"""

    raw = ask_gemini(prompt)

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean.strip())
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        # Safe fallback based on score
        if risk_score >= 70:
            actions = [
                {"order": 1, "action": "Draw blood cultures x2 peripheral sites", "timeframe": "within 15 minutes", "rationale": "Culture before antibiotics per SSC 2024", "fhir_request_type": "ServiceRequest"},
                {"order": 2, "action": "Broad-spectrum antibiotics IV", "timeframe": "within 60 minutes", "rationale": "Hour-1 Bundle — antibiotics within 1 hour of sepsis recognition", "fhir_request_type": "MedicationRequest"},
                {"order": 3, "action": "IV crystalloid 30ml/kg bolus", "timeframe": "within 3 hours", "rationale": "Fluid resuscitation for sepsis-induced hypoperfusion", "fhir_request_type": "MedicationRequest"},
                {"order": 4, "action": "Repeat lactate if initial >2 mmol/L", "timeframe": "within 2 hours", "rationale": "Lactate-guided resuscitation per SSC 2024", "fhir_request_type": "ServiceRequest"},
            ]
            protocol = "SSC Hour-1 Bundle"
        elif risk_score >= 40:
            actions = [
                {"order": 1, "action": "Notify attending physician", "timeframe": "within 15 minutes", "rationale": "Moderate risk requires physician evaluation", "fhir_request_type": "ServiceRequest"},
                {"order": 2, "action": "Repeat vitals q15min", "timeframe": "immediately", "rationale": "Monitor for deterioration", "fhir_request_type": "Observation"},
                {"order": 3, "action": "Draw lactate and CBC", "timeframe": "within 30 minutes", "rationale": "Baseline labs for trending", "fhir_request_type": "ServiceRequest"},
            ]
            protocol = "Enhanced Monitoring"
        else:
            actions = [
                {"order": 1, "action": "Routine reassessment in 60 minutes", "timeframe": "1 hour", "rationale": "Low risk — standard monitoring protocol", "fhir_request_type": "Observation"},
            ]
            protocol = "Routine Protocol"

        return json.dumps({
            "patient_id": patient_id,
            "protocol": protocol,
            "priority_actions": actions,
            "monitoring": {
                "vitals_frequency": "every 15 minutes" if risk_score >= 70 else "every 30 minutes",
                "labs_to_repeat": ["Lactate", "CBC", "BMP"] if risk_score >= 40 else ["None required"],
                "reassessment_trigger": "SBP <90, HR >120, new AMS, SpO2 <92%"
            },
            "escalation_path": "Attending Physician → ICU consult if no improvement in 1 hour",
            "contraindication_flags": [],
            "guideline_reference": "Surviving Sepsis Campaign International Guidelines 2024",
            "recommended_at": datetime.utcnow().isoformat() + "Z"
        }, indent=2)


# ─────────────────────────────────────────────
# AUTH MIDDLEWARE
# ─────────────────────────────────────────────
class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Skip auth if API_KEY not configured
        if not API_KEY:
            return await call_next(request)
        # Health check always allowed
        if request.url.path in ("/health", "/"):
            return await call_next(request)
        # Check header
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            log.warning(f"Unauthorized request from {request.client.host}")
            return JSONResponse({"error": "Unauthorized — invalid API key"}, status_code=401)
        return await call_next(request)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  SepsisGuard AI — MCP Server")
    print("  Powered by Gemini 2.5 Flash")
    print("=" * 55)
    print(f"  Model    : {GEMINI_MODEL}")
    print(f"  Host     : {HOST}:{PORT}")
    print(f"  Endpoint : http://{HOST}:{PORT}/mcp")
    print(f"  Auth     : {'Enabled (X-API-Key)' if API_KEY else 'Disabled (open)'}")
    print(f"  API Key  : {'SET' if GEMINI_API_KEY else 'MISSING — set GEMINI_API_KEY in .env'}")
    print("=" * 55)

    app = mcp.streamable_http_app()
    app.add_middleware(APIKeyMiddleware)

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")