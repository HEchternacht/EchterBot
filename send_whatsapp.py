import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["KAPSO_API_KEY"]
PHONE_NUMBER_ID = os.environ["KAPSO_PHONE_NUMBER_ID"]

def send_text(to: str, body: str) -> dict:
    url = f"https://api.kapso.ai/meta/whatsapp/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    result = send_text("5524993003688", "Hello from Kapso! This is a test message.")
    print(result)
