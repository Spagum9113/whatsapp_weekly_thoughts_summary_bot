# this script is to recieve the messages from whatsapp and then store it into supabase


from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from supabase_client import supabase
from datetime import datetime, timezone
from dotenv import load_dotenv
from twilio.request_validator import RequestValidator
from send_twilio import send_whatsapp_message
import uvicorn
import os
import json

# get the env keys
load_dotenv()

# start the server
app = FastAPI()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "123451")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_TOKEN")


# func to validate twilio signature for security
# def _is_valid_twilio_request(request: Request, body: dict) -> bool:

#     if not TWILIO_AUTH_TOKEN:
#         return True

#     validator = RequestValidator(TWILIO_AUTH_TOKEN)
#     signature = request.headers.get("X-Twilio-Signature", "")

#     url = str(request.url)

#     return validator.validate(url, body, signature)


# webhook to read the incoming messages
@app.post("/webhook-twilio")
async def twilio_whatsapp_webhook(request: Request):

    print("this webhook is working 1")

    form = dict((await request.form()).items())

    # extract the common fields
    body = form.get("Body")
    from_number = form.get("From", "")
    wa_id = form.get("WaId", "")
    profile = form.get("ProfileName", "")

    print("---- Incoming WhatsApp ----")
    print(f"From: {from_number} (wa_id={wa_id}, name={profile})")
    print(f"Text: {body}")

    print("---------------------------")

    # call function to save note into supabase
    if body:
        saved_note = save_note(
            user_id=wa_id,
            text=body,
            sid=form.get("MessageSid", "")
        )

        print(f"Saved note: {saved_note}")

    # send response so i know it was recieved
    send_whatsapp_message('kk')

    # Fast ack (no reply)
    return PlainTextResponse(status_code=200, content="OK")


# store the message into supabase
def save_note(*, user_id: str, text: str, sid: str):
    row = {
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_text": text,
        "sid": sid,
        "source": "whatsapp",
    }
    # Upsert prevents duplicates if the same sid arrives again
    response = supabase.table("notes").upsert(
        row, on_conflict="id"
    ).execute()
    return response.data[0] if response.data else row


# run it
if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8000)
