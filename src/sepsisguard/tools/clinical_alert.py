import json
import logging
from datetime import datetime
from typing import Optional
from ..services.gemini_client import gemini_client
from ..utils.helpers import clean_json_response

log = logging.getLogger("sepsisguard.tools.alert")

async def generate_clinical_alert_tool(
    patient_id: str,
    risk_score: int,
    risk_level: str,
    reasoning_chain: str,
    key_signals: Optional[str] = None
) -> str:
    """
    Generates a structured clinical alert for bedside staff and charge nurses.
    """
    log.info(f"Generating clinical alert for patient: {patient_id}")

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

    raw_response = gemini_client.ask(prompt)
    cleaned_response = clean_json_response(raw_response)

    try:
        json.loads(cleaned_response)
        return cleaned_response
    except json.JSONDecodeError:
        log.error("Gemini returned invalid JSON for clinical alert")
        return json.dumps({
            "error": "Failed to generate structured clinical alert",
            "raw_output": raw_response
        })
