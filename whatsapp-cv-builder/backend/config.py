# ---------------------------------------------------------------
# backend/config.py
# WHY THIS FILE EXISTS:
#   Loads all settings from backend/.env in ONE place. Every other
#   backend file imports its settings from here instead of reading
#   environment variables on its own. This means:
#     - .env is loaded once, not scattered across many files
#     - if a required key is missing, we find out immediately at
#       startup with a clear error, not halfway through a request
#
# WHAT IT DOES:
#   - Reads OpenAI and WhatsApp values from .env
#   - (MongoDB values are read inside db/connection.py, which already
#     works, so we leave that as-is to avoid rewriting a tested file)
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - services/openai_service.py imports OPENAI_API_KEY
#   - services/whatsapp_service.py imports WHATSAPP_TOKEN and
#     WHATSAPP_PHONE_NUMBER_ID
#   - routes/webhook.py imports WHATSAPP_VERIFY_TOKEN
# ---------------------------------------------------------------

import os
from dotenv import load_dotenv

# Load backend/.env into the environment once.
load_dotenv()

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Meta WhatsApp Cloud API ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


# Fail loudly at startup if any required value is missing, so a
# blank key never causes a confusing error later during the demo.
def check_config():
    """
    Confirm every required setting is present. Called once when the
    Flask app starts. Prints which keys are missing instead of
    failing silently.
    """
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not WHATSAPP_TOKEN:
        missing.append("WHATSAPP_TOKEN")
    if not WHATSAPP_PHONE_NUMBER_ID:
        missing.append("WHATSAPP_PHONE_NUMBER_ID")
    if not WHATSAPP_VERIFY_TOKEN:
        missing.append("WHATSAPP_VERIFY_TOKEN")

    if missing:
        raise ValueError(
            "Missing values in backend/.env: " + ", ".join(missing)
        )
    return True