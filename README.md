# WhatsApp Summary Bot

A Python-based WhatsApp bot that captures your messages via Twilio, stores them in Supabase, and generates weekly AI-powered digests using OpenAI.

## Features
- 📱 Receive WhatsApp messages through Twilio webhooks  
- 💾 Store notes in Supabase  
- 🤖 Create weekly summaries with OpenAI  
- 🔄 Automate digest sending every Sunday  
- 💰 Track API usage and costs  

**Architecture:**  
`WhatsApp → Twilio → FastAPI → Supabase → OpenAI → Weekly Digest`
