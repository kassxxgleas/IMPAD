"""
Configuration for LLM modes and API settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
