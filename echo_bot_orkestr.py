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


def handler(event):
    """Orkestr serverless function handler for WhatsApp webhooks."""
    # Parse the webhook payload
    data = event.get("body", {}) if isinstance(event.get("body"), dict) else {}
    
    # Handle Kapso webhook format
    event_type = data.get("event") or data.get("type")
    
    if event_type == "whatsapp.message.received":
        message_data = data.get("data", {})
        from_number = message_data.get("phone_number") or message_data.get("from")
        message_text = message_data.get("text", {}).get("body")
        
        if from_number and message_text:
            reply_body = f"Echo: {message_text}"
            try:
                send_text(from_number, reply_body)
            except Exception as e:
                print(f"Error sending reply: {e}")
                
        return {
            "statusCode": 200,
            "body": {"status": "processed"}
        }
    
    elif event_type == "whatsapp.meta.webhook" or "entry" in data:
        # Handle raw Meta webhook payload
        entries = data.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                if change.get("field") == "messages":
                    values = change.get("values", {})
                    messages = values.get("messages", [])
                    for msg in messages:
                        from_number = msg.get("from")
                        text_data = msg.get("text", {})
                        message_text = text_data.get("body")
                        
                        if from_number and message_text:
                            reply_body = f"Echo: {message_text}"
                            try:
                                send_text(from_number, reply_body)
                            except Exception as e:
                                print(f"Error sending reply: {e}")
                                
        return {
            "statusCode": 200,
            "body": {"status": "processed"}
        }
    
    else:
        # Ignore other events
        return {
            "statusCode": 200,
            "body": {"status": "ignored"}
        }
