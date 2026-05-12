import json
import logging
from datetime import datetime
from typing import Optional
from ..services.gemini_client import gemini_client
from ..utils.helpers import clean_json_response

log = logging.getLogger("sepsisguard.tools.treatment")

async def recommend_bundle_actions_tool(
    patient_id: str,
    risk_score: int,
    risk_level: str,
    patient_context: Optional[str] = None
) -> str:
    """
    Recommends Surviving Sepsis Campaign (SSC 2024) bundle actions based on risk score.
    """
    log.info(f"Recommending bundle actions for patient: {patient_id}")

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

    raw_response = gemini_client.ask(prompt)
    cleaned_response = clean_json_response(raw_response)

    try:
        json.loads(cleaned_response)
        return cleaned_response
    except json.JSONDecodeError:
        log.error("Gemini returned invalid JSON for treatment recommendations")
        return json.dumps({
            "error": "Failed to generate structured treatment recommendations",
            "raw_output": raw_response
        })
