"""Shared utilities for WhatsApp echo bot."""

import os
import logging
import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration with validation
API_KEY = os.environ.get("KAPSO_API_KEY")
PHONE_NUMBER_ID = os.environ.get("KAPSO_PHONE_NUMBER_ID")

if not API_KEY:
    raise ValueError("KAPSO_API_KEY environment variable is required")
if not PHONE_NUMBER_ID:
    raise ValueError("KAPSO_PHONE_NUMBER_ID environment variable is required")

# Constants
API_BASE_URL = "https://api.kapso.ai/meta/whatsapp/v24.0"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


def send_text(to: str, body: str) -> dict:
    """Send a WhatsApp text message via Kapso API.

    Args:
        to: Recipient phone number
        body: Message text

    Returns:
        Response JSON from API

    Raises:
        requests.exceptions.HTTPError: If API returns error status
        ValueError: If to or body is empty
    """
    if not to:
        raise ValueError("Recipient phone number cannot be empty")
    if not body:
        raise ValueError("Message body cannot be empty")

    url = f"{API_BASE_URL}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    logger.info(f"Sending message to {to}")
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    logger.info(f"Message sent successfully to {to}")
    return resp.json()
