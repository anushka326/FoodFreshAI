"""
FoodFresh AI - Test Gemini Connection Script
Verifies Google GenAI connection safely without exposing the API key or recording chats.
Conforms to Part 25 specification.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env if present
for env_path in [PROJECT_ROOT / ".env", PROJECT_ROOT / "backend" / ".env"]:
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass


def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()

    if not api_key:
        print("GEMINI_API_KEY not found in environment.")
        sys.exit(1)

    # Confirm key detected without printing the key
    print("Gemini API key detected.")

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'FreshoBuddy connection verified!' in 5 words or less."
        )

        if not response or not response.text:
            print("No response received from Gemini model.")
            sys.exit(1)

        print("Gemini API connection successful.")
        print("Model response received successfully.")
        sys.exit(0)

    except Exception as e:
        print(f"Gemini API connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
