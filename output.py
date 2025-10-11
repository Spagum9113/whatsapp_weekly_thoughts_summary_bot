# this script is to take all messages from last week and get the weekly summaries and send output back into whatsapp
import os
import requests
import aiohttp
import asyncio
import json
from dotenv import load_dotenv
from supabase_client import supabase
from datetime import datetime, timezone, timedelta
from openai import OpenAI
from send_twilio import send_whatsapp_message

# load the env
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# set up openai
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# VARIABLES
INPUT_PRICE_USD = 0.25   # input tokens
OUTPUT_PRICE_USD = 2.00   # output tokens
USD_TO_AUD = 1.55


# main function
def main():

    # get the data first by querying supabase
    last_week_messages = get_weekly_summary()

    # get the week_id
    week_id = get_week_id()

    # process it with openai
    summary_text, cost_aud, input_tokens, output_tokens = send_to_openai(
        week_id, last_week_messages)

    # save it into supabase weekly_digest table
    save_note(summary_text, cost_aud, input_tokens, output_tokens, week_id)

    # send the actual whatsapp output
    data = get_text_message_input(recipient=RECIPIENT_WAID, text=summary_text)
    response = send_whatsapp_message(summary_text)


# Make the week_id
def get_week_id(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)
    year, week, _ = dt.isocalendar()
    print(f"{year}-W{week:02d}")
    return f"{year}-W{week:02d}"


def get_weekly_summary():

    # calculate 7 days ago VAR
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    start_date = one_week_ago.isoformat()

    # query supabase to get all messages from the last week
    response = supabase.table("notes").select("raw_text, created_at") \
        .gte("created_at", start_date) \
        .order("created_at", desc=False) \
        .execute()

    # extract purely the raw text alone
    raw_text_combined = ""

    print(response.data)
    return (response.data)


def send_to_openai(week_id, text):

    # send to openai
    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                        "content": """
    You summarize a week of my notes into an ultra-actionable WhatsApp digest.
    Rules:
    - STRICTLY keep under 1200 characters including spacing (so it fits on WhatsApp).
    - Follow the exact format below.

    Format:

    🗓 Weekly Digest — {week_id}

    📌 {5–7 word title}

    🧾 Summary
    {2–4 sentences, plain, first-person}

    ✨ Themes (top 2)
    1) {theme 1} — “{evidence quote}”
    2) {theme 2} — “{evidence quote}”


    🤖 AI's Thoughts
    {Write 2–3 sentences that provide analysis, reflection, potential action stpes and constructive prompts. Connect patterns from the week, highlight blind spots or tensions, and suggest ways to deepen thinking next week. The tone should read like a thoughtful mini-analysis of my ideas, noticing what I might not see such as patterns, trade-offs, or risks, while reflecting back the underlying “why” behind my actions and how they align with my goals. End by offering one or two provocative questions or directions that push me to think further.}
    """
            },
            {
                "role": "user",
                "content": f"Here are my raw notes for the week {week_id}: {text}. Please summarize into the WhatsApp digest format described above."
            }
        ]

    )

    # 1) Extract the summary text
    summary_text = response.output_text
    print(summary_text)

    # 2) Extract the tokens
    usage = getattr(response, "usage")
    input_tokens = getattr(usage, "input_tokens")
    output_tokens = getattr(usage, "output_tokens")

    # 3) calc the costs in AUD
    cost_usd = (input_tokens/1000000.0)*INPUT_PRICE_USD + \
        (output_tokens/1000000.0)*OUTPUT_PRICE_USD
    cost_aud = round(cost_usd * USD_TO_AUD, 4)
    print(f'the cost is {cost_aud}')

    # return the summary text, cost_aud, input_tokens and output_tokens
    return summary_text, cost_aud, input_tokens, output_tokens


# store the message into supabase
def save_note(summary_text: str, cost_aud: float, input_tokens: int, output_tokens: int, week_id: str | None = None):
    row = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary_text": summary_text,
        "cost_aud": cost_aud,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model": "gpt-5-mini",
        "week_id": week_id,
    }
    # Upsert prevents duplicates if the same sid arrives again
    response = supabase.table("weekly_digests").upsert(
        row, on_conflict="id").execute()
    return response.data[0] if response.data else row


# Say WHO and WHAT i want to send
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

# Sends the actual whatsapp message


# def send_message(data):

#     url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "application/json",

#     }

#     response = requests.post(url, headers=headers, json=data)

#     print("return requests")
#     print(response.status_code)

#     return response


# activate
main()
