import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["KAPSO_API_KEY"]
PHONE_NUMBER_ID = os.environ["KAPSO_PHONE_NUMBER_ID"]

app = FastAPI(title="WhatsApp Echo Bot")


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


@app.post("/webhook")
async def webhook(request: Request):
    """Receive incoming WhatsApp messages and echo them back."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Parse Kapso webhook payload
    event = data.get("event") or data.get("type")
    
    if event == "whatsapp.message.received":
        message_data = data.get("data", {})
        from_number = message_data.get("phone_number") or message_data.get("from")
        message_text = message_data.get("text", {}).get("body")
        
        if not from_number or not message_text:
            return JSONResponse(status_code=200, content={"status": "ignored"})
        
        # Echo the message back
        reply_body = f"Echo: {message_text}"
        try:
            send_text(from_number, reply_body)
        except Exception as e:
            print(f"Error sending reply: {e}")
            
        return JSONResponse(status_code=200, content={"status": "processed"})
    
    elif event == "whatsapp.meta.webhook":
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
                                
        return JSONResponse(status_code=200, content={"status": "processed"})
    
    else:
        # Ignore other events
        return JSONResponse(status_code=200, content={"status": "ignored"})


@app.get("/webhook/verify")
async def webhook_verify():
    """Verify webhook endpoint (for Meta webhook verification)."""
    mode = os.environ.get("WEBHOOK_VERIFY_MODE", "")
    token = os.environ.get("WEBHOOK_VERIFY_TOKEN", "")
    verify_token = os.environ.get("VERIFY_TOKEN", token)
    
    if mode == "subscribe":
        hub_mode = os.environ.get("HUB_MODE", "")
        hub_verify_token = os.environ.get("HUB_VERIFY_TOKEN", "")
        hub_challenge = os.environ.get("HUB_CHALLENGE", "")
        
        if hub_verify_token == verify_token:
            return JSONResponse(status_code=200, content={"hub_challenge": hub_challenge})
        else:
            raise HTTPException(status_code=403, detail="Invalid verify token")
    
    return JSONResponse(status_code=200, content={"status": "ok"})
