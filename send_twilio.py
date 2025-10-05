from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()


TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
NUMBER_TO = os.getenv("NUMBER_TO")


client = Client(TWILIO_SID, TWILIO_TOKEN)

# msg = client.messages.create(
#     from_=TWILIO_FROM,
#     to=NUMBER_TO,
#     body="Hello from A Crunchy Design via Twilio WhatsApp!"
# )


# function to actually send the whatsapp msg
def send_whatsapp_message(summary_text):

    msg = client.messages.create(
        from_=TWILIO_FROM,
        to=NUMBER_TO,
        body=summary_text

    )

    print(f"Message sent! SID: {msg.sid}, Status: {msg.status}")
    return msg
