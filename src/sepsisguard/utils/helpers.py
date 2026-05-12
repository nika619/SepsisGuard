import json
import logging
from typing import Optional, Any

log = logging.getLogger("sepsisguard.utils")

def parse_sharp_context(context_json: Optional[Any]) -> dict:
    """Parse SHARP context JSON string or dict into dict."""
    if not context_json:
        return {}
    try:
        if isinstance(context_json, dict):
            return context_json
        return json.loads(str(context_json))
    except Exception as e:
        log.error(f"Failed to parse SHARP context: {e}")
        return {}

def clean_json_response(raw_text: str) -> str:
    """Clean Gemini response to ensure valid JSON."""
    clean = raw_text.strip()
    if clean.startswith("```"):
        # Remove markdown code blocks
        parts = clean.split("```")
        if len(parts) >= 3:
            clean = parts[1]
            if clean.startswith("json"):
                clean = clean[4:]
    return clean.strip()
