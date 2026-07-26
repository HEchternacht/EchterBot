"""FastAPI web application for WhatsApp echo bot."""

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from common import send_text, logger

app = FastAPI(title="WhatsApp Echo Bot")


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
            logger.warning("Missing from_number or message_text, ignoring")
            return JSONResponse(status_code=200, content={"status": "ignored"})

        # Echo the message back
        reply_body = f"Echo: {message_text}"
        try:
            send_text(from_number, reply_body)
        except Exception as e:
            logger.error(f"Error sending reply: {e}")

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
                                logger.error(f"Error sending reply: {e}")

        return JSONResponse(status_code=200, content={"status": "processed"})

    else:
        # Ignore other events
        logger.debug(f"Ignoring event type: {event}")
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
            logger.info("Webhook verification successful")
            return JSONResponse(status_code=200, content={"hub_challenge": hub_challenge})
        else:
            logger.warning("Invalid verify token")
            raise HTTPException(status_code=403, detail="Invalid verify token")

    return JSONResponse(status_code=200, content={"status": "ok"})
