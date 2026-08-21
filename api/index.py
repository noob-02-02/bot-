import os
import subprocess
import logging
from fastapi import FastAPI, Request
import requests

# FastAPI app instance for Vercel
app = FastAPI()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Aapka Bot Token aur Admin ID
TOKEN = "8868389563:AAEK2-SWGgmt5B88oR6Ny3KbdmcpHLvb-0U"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
ADMIN_USER_ID = 8372837217

HOSTING_DIR = "my_hosting_server"
SCRIPTS_DIR = "live_scripts"

for folder in [HOSTING_DIR, SCRIPTS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

@app.post("/api/index")
async def webhook(req: Request):
    data = await req.json()
    
    if "message" in data:
        message = data["message"]
        user_id = message["from"]["id"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Admin check
        if not is_admin(user_id):
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "⛔ Aapko is bot ko use karne ki anumati (permission) nahi hai."
            })
            return {"status": "ok"}
            
        # Commands handling
        if text.startswith("/start"):
            reply = (
                "👋 **Welcome to your Vercel Hosting Bot!**\n\n"
                "**Available Commands:**\n"
                "📁 `/create <name>` - Naya folder banayein\n"
                "📂 `/list` - Sabhi projects ki list dekhein"
            )
        elif text.startswith("/create"):
            parts = text.split()
            if len(parts) < 2:
                reply = "⚠️ Kripya project ka naam dein. Example: `/create mywebsite`"
            else:
                project_name = parts[1]
                project_path = os.path.join(HOSTING_DIR, project_name)
                try:
                    if not os.path.exists(project_path):
                        os.makedirs(project_path)
                        index_file = os.path.join(project_path, "index.php")
                        with open(index_file, "w") as f:
                            f.write("<?php echo 'Hello from Vercel Bot!'; ?>")
                        reply = f"✅ Success! Project **'{project_name}'** create ho gaya hai."
                    else:
                        reply = f"⚠️ Project **'{project_name}'** pehle se exist karta hai!"
                except Exception as e:
                    reply = f"❌ Error aaya: {str(e)}"
        elif text.startswith("/list"):
            try:
                projects = os.listdir(HOSTING_DIR)
                if not projects:
                    reply = "📁 Aapke hosting server par abhi koi project nahi hai."
                else:
                    project_list = "\n".join([f"🔹 {p}" for p in projects])
                    reply = f"📂 **Aapke Hosted Projects:**\n\n{project_list}"
            except Exception as e:
                reply = f"❌ Error: {str(e)}"
        else:
            reply = "🤖 Vercel serverless mode active hai. Kripya `/start`, `/create`, ya `/list` command ka use karein."

        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply,
            "parse_mode": "Markdown"
        })
        
    return {"status": "ok"}
