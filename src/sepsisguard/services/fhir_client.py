import httpx
import logging
import base64
from typing import Optional

log = logging.getLogger("sepsisguard.fhir")

class FHIRClient:
    @staticmethod
    async def fetch_patient_documents(fhir_url: str, patient_id: str, token: Optional[str] = None) -> str:
        """Fetch patient documents from a FHIR server."""
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{fhir_url.rstrip('/')}/DocumentReference?patient={patient_id}"
                log.info(f"Fetching FHIR documents for patient {patient_id} from {url}")
                r = await client.get(url, headers=headers)
                r.raise_for_status()
                bundle = r.json()
                
                docs = []
                for entry in bundle.get("entry", []):
                    resource = entry.get("resource", {})
                    for content in resource.get("content", []):
                        data = content.get("attachment", {}).get("data", "")
                        if data:
                            try:
                                # Try decoding base64 if it looks like it
                                docs.append(base64.b64decode(data).decode("utf-8"))
                            except Exception:
                                docs.append(data)
                
                if docs:
                    return "\n\n---\n\n".join(docs)
                return ""
        except Exception as e:
            log.warning(f"FHIR fetch failed for patient {patient_id}: {e}")
            return ""

# Singleton instance
fhir_client = FHIRClient()
