"""Standalone script for testing WhatsApp message sending."""

import sys
from common import send_text, logger


if __name__ == "__main__":
    # Test number from original code
    test_number = "5524993003688"
    test_message = "Hello from Kapso! This is a test message."

    logger.info(f"Sending test message to {test_number}")
    try:
        result = send_text(test_number, test_message)
        print(result)
    except Exception as e:
        logger.error(f"Failed to send test message: {e}")
        sys.exit(1)
