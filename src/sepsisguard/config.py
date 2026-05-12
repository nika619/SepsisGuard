import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    API_KEY = os.getenv("API_KEY", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    GEMINI_MODEL = "gemini-2.5-flash"
    
    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            print("WARNING: GEMINI_API_KEY is not set. AI features will fail.")
