# ---------------------------------------------------------------
# backend/services/whatsapp_service.py
# WHY THIS FILE EXISTS:
#   Sends WhatsApp messages OUT to candidates via Meta's WhatsApp
#   Cloud API. This is the only place the project sends WhatsApp
#   messages. It is used for two things:
#     1. Replying to the candidate during the 5-question flow
#     2. Sending the job alert when an employer publishes a job
#
# WHAT IT DOES:
#   - Takes a recipient number and a text message
#   - POSTs it to Meta's Graph API using our token
#   - Returns True if sent, False if something went wrong
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - Reads WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID from config
#   - routes/webhook.py calls send_message() to reply to candidates
#   - matching.py (on job publish) calls send_message() for alerts
# ---------------------------------------------------------------

import requests
import config

# Meta's Graph API endpoint for sending messages. The phone number ID
# (from .env) identifies WHICH WhatsApp business number we send from.
URL = f"https://graph.facebook.com/v20.0/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"


def send_message(to_number, message_text):
    """
    Send one WhatsApp text message.

    to_number:    the recipient's number in international format,
                  digits only, no + (e.g. "27821234567").
    message_text: the text to send.

    Returns True if Meta accepted the message, False otherwise.
    """

    # The token proves we're allowed to send from this number.
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    # Meta's required message shape for a plain text message.
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text},
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=10)
        # Meta returns 200 on success. Anything else, we print the
        # reason so we can see what went wrong during the demo.
        if response.status_code == 200:
            return True
        else:
            print("WhatsApp send failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("WhatsApp send error:", e)
        return False