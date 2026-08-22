import os
import logging
from urllib.parse import parse_qs, urlparse
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Setup FastAPI
app = FastAPI()

TOKEN = "8761704094:AAHYOLC_IRlct6YukFPYtTJlRZRmNCfEDGI"

# Telegram Application Setup
telegram_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text(
        "👋 Hello! Mujhe koi bhi URL bhejiye, main usme se sare parameters "
        "(jaise aff_id, click_id, etc.) alag karke de dunga."
    )

async def extract_parameters(update: Update, context):
    user_text = update.message.text.strip()
    parsed_url = urlparse(user_text)
    
    if not parsed_url.scheme or not parsed_url.netloc:
        query_string = user_text if "?" in user_text else f"?{user_text}"
        parsed_url = urlparse(f"http://dummy.com/{query_string}")

    query_params = parse_qs(parsed_url.query)

    if not query_params:
        await update.message.reply_text("❌ Is URL ya text mein koi bhi parameters nahi mile.")
        return

    response = "🔍 **Extracted Parameters:**\n\n"
    for key, values in query_params.items():
        response += f"• **{key}**: `{values[0]}`\n"

    if parsed_url.netloc not in ["dummy.com", ""]:
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        response = f"🌐 **Base URL:**\n`{base_url}`\n\n" + response

    await update.message.reply_text(response, parse_mode="Markdown")

# Add Handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), extract_parameters))

@app.post("/")
@app.post("/api/index")
async def webhook(request: Request):
    data = await request.json()
    
    async with telegram_app:
        await telegram_app.start()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        await telegram_app.stop()
        
    return {"status": "ok"}

@app.get("/")
def home():
    return {"message": "Bot is running fine!"}
