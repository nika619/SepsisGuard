import logging
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import Config
from .tools.risk_analysis import compute_sepsis_risk_tool
from .tools.clinical_alert import generate_clinical_alert_tool
from .tools.treatment_recommendations import recommend_bundle_actions_tool

log = logging.getLogger("sepsisguard.server")

# Initialize FastMCP
mcp = FastMCP("SepsisGuard AI")

# Register Tools
@mcp.tool(name="compute_sepsis_risk")
async def compute_sepsis_risk(
    patient_id: str,
    fhir_context: str = None,
    demo_scenario: str = None
) -> str:
    """
    Analyzes patient data (vitals, labs, notes) to compute sepsis risk (0-100).
    Includes reasoning chain and key clinical signals.
    """
    return await compute_sepsis_risk_tool(patient_id, fhir_context, demo_scenario)

@mcp.tool(name="generate_clinical_alert")
async def generate_clinical_alert(
    patient_id: str,
    risk_score: int,
    risk_level: str,
    reasoning_chain: str,
    key_signals: str = None
) -> str:
    """
    Formats structured bedside alerts for nursing staff with immediate actions.
    """
    return await generate_clinical_alert_tool(patient_id, risk_score, risk_level, reasoning_chain, key_signals)

@mcp.tool(name="recommend_bundle_actions")
async def recommend_bundle_actions(
    patient_id: str,
    risk_score: int,
    risk_level: str,
    patient_context: str = None
) -> str:
    """
    Returns treatment recommendations aligned with SSC 2024 guidelines.
    """
    return await recommend_bundle_actions_tool(patient_id, risk_score, risk_level, patient_context)


# Auth Middleware
class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not Config.API_KEY:
            return await call_next(request)
        
        if request.url.path in ("/health", "/"):
            return await call_next(request)
            
        key = request.headers.get("X-API-Key", "")
        if key != Config.API_KEY:
            log.warning(f"Unauthorized access attempt from {request.client.host}")
            return JSONResponse({"error": "Unauthorized — invalid API key"}, status_code=401)
        return await call_next(request)

def create_app():
    """Create and configure the Starlette app from FastMCP."""
    app = mcp.streamable_http_app()
    app.add_middleware(APIKeyMiddleware)
    return app
