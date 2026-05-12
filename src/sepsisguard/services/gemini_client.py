import logging
from google import genai
from google.genai import types
from ..config import Config

log = logging.getLogger("sepsisguard.gemini")

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model = Config.GEMINI_MODEL

    def ask(self, prompt: str, temperature: float = 0.2) -> str:
        """Send a prompt to Gemini and return the text response."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=1500,
                )
            )
            return response.text.strip()
        except Exception as e:
            log.error(f"Gemini API error: {e}")
            raise RuntimeError(f"Gemini API error: {e}")

# Singleton instance
gemini_client = GeminiClient()
