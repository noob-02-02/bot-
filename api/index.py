import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN = "8868389563:AAEK2-SWGgmt5B88oR6Ny3KbdmcpHLvb-0U"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
ADMIN_USER_ID = 8372837217

@app.post("/api/index")
async def webhook(req: Request):
    try:
        data = await req.json()
        
        if "message" in data:
            message = data["message"]
            user_id = message["from"]["id"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            # Admin check
            if user_id != ADMIN_USER_ID:
                requests.post(f"{TELEGRAM_API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "⛔ Aapko is bot ko use karne ki anumati nahi hai."
                })
                return {"status": "ok"}
                
            if text.startswith("/start"):
                reply = (
                    "👋 **Welcome to your Vercel Bot!**\n\n"
                    "**Commands:**\n"
                    "🔹 `/start` - Bot start karein\n"
                    "🔹 `/help` - Help message dekhein"
                )
            else:
                reply = f"🤖 Aapne kaha: {text}"

            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply,
                "parse_mode": "Markdown"
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        
    return {"status": "ok"}
