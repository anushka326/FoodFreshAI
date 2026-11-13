import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if exists
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Configuration variables with defaults
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///./{BASE_DIR / 'foodfresh.db'}")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

