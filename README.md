# WhatsApp Echo Bot

A simple WhatsApp bot that echoes back received messages via the Kapso API.

## Features

- Echo bot: Receives WhatsApp messages and sends them back with "Echo: " prefix
- Dual deployment support:
  - FastAPI web server (main.py) for traditional hosting
  - Serverless handler (echo_bot_orkestr.py) for Orkestr platform
- Proper error handling and logging
- Environment variable validation

## Requirements

- Python 3.8+
- Kapso API key and phone number ID

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your credentials:
   ```env
   KAPSO_API_KEY=your_api_key_here
   KAPSO_PHONE_NUMBER_ID=your_phone_number_id_here
   ```

## Usage

### FastAPI Server

Run the web server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server exposes:
- `POST /webhook` - Receive and process WhatsApp messages
- `GET /webhook/verify` - Webhook verification endpoint

### Orkestr Serverless

Deploy `echo_bot_orkestr.py` to Orkestr platform. The `handler()` function will be called with webhook events.

### Test Script

Send a test message:
```bash
python send_whatsapp.py
```

## Project Structure

```
wsp/
├── common.py              # Shared utilities (send_text, logging, config)
├── main.py                # FastAPI web application
├── echo_bot_orkestr.py    # Serverless handler for Orkestr
├── send_whatsapp.py       # Standalone test script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed)
└── README.md              # This file
```

## API Reference

### `send_text(to: str, body: str) -> dict`

Send a WhatsApp text message.

**Args:**
- `to`: Recipient phone number
- `body`: Message text

**Returns:**
- Response JSON from Kapso API

**Raises:**
- `ValueError`: If to or body is empty
- `requests.exceptions.HTTPError`: If API returns error status

## Logging

The bot uses Python's logging module. Logs are output to stdout with timestamps.

## Error Handling

- Missing environment variables: Application fails fast on startup with clear error message
- Invalid webhook payloads: Returns 200 with "ignored" status
- API errors: Logged and returned as 200 (webhooks should always acknowledge)

## Deployment

### FastAPI (traditional hosting)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or use a production server like Gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Orkestr (serverless)

Upload `echo_bot_orkestr.py` to Orkestr platform. Ensure environment variables are set in the Orkestr dashboard.

## Security

- Never commit `.env` file or API keys
- Use HTTPS for webhook endpoint
- Validate webhook verify tokens in production

## License

MIT
