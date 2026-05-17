import requests
from django.conf import settings
import json


def send_error_to_discord(message):

    if not settings.DEBUG:
        webhook_url = settings.WEBHOOK_URL 

        if isinstance(message, dict):
            formatted_message = f"```json\n{json.dumps(message, indent=2)}\n```"

        else:
            formatted_message = str(message)
        data = {
            "content": f"{formatted_message}"
        }

        try:
            requests.post(webhook_url, json=data, timeout=5)

        except requests.exceptions.RequestException as e:
            print(f"Failed to send alert to Discord: {e}")

    else:

        if not webhook_url:
            print("\n--- [DEBUG MODE] DISCORD ALERT BYPASSED ---")
            print(f"Payload: {message}")
            print("-------------------------------------------\n")

            return