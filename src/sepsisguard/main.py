import uvicorn
import logging
from .config import Config
from .server import create_app

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log = logging.getLogger("sepsisguard.main")

def main():
    """Main entry point for the SepsisGuard AI server."""
    Config.validate()
    
    print("=" * 60)
    print("  ◈ SEPSISGUARD AI ◈ Detect Deterioration. Defend Every Hour.")
    print("=" * 60)
    print(f"  Model    : {Config.GEMINI_MODEL}")
    print(f"  Host     : {Config.HOST}:{Config.PORT}")
    print(f"  Auth     : {'Enabled' if Config.API_KEY else 'Disabled (Development Mode)'}")
    print("=" * 60)

    app = create_app()
    uvicorn.run(app, host=Config.HOST, port=Config.PORT, log_level="info")

if __name__ == "__main__":
    main()
