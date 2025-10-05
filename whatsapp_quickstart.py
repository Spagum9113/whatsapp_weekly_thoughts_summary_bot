# this script is just to test sending messages

import json
from dotenv import load_dotenv
import os
import requests
import aiohttp
import asyncio

# Load env variables
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")


# Send a template whatsapp msg

def send_whatsapp_message():
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_WAID,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},

    }

    response = requests.post(url, headers=headers, json=data)

    return response


# call the func
# response = send_whatsapp_message()
# print(response.status_code)
# print(response.json())


# func to send custom messages
def get_text_message_input(recipient, text):
    return {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text
        }
    }


def send_message(data):

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",

    }

    response = requests.post(url, headers=headers, json=data)

    print("return requests")
    print(response.status_code)

    return response


data = get_text_message_input(
    recipient=RECIPIENT_WAID, text="hi stella")

response = send_message(data)
