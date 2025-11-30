"""
Configuration for LLM modes and API settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / '.env'
print(f"DEBUG: Loading .env from {env_path}")
load_dotenv(dotenv_path=env_path)

# Check if key is loaded
key = os.getenv("OPENAI_API_KEY")
print(f"DEBUG: OPENAI_API_KEY found: {bool(key)}")

# Режим роботи: "fake" або "real"
LLM_MODE = os.getenv("LLM_MODE", "fake")

# OpenAI конфіги
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.1

# Retry логіка
MAX_RETRIES = 3
TIMEOUT_SECONDS = 10

# Debug
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
