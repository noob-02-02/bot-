import os
import logging
from html import escape
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

    # keep_blank_values=True ensures empty parameters like af_ip= are also caught
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)

    if not query_params:
        await update.message.reply_text("❌ Is URL ya text mein koi bhi parameters nahi mile.")
        return

    response = "🔍 <b>Extracted Parameters:</b>\n\n"
    for key, values in query_params.items():
        val = escape(values[0]) if values[0] else "<i>(empty)</i>"
        response += f"• <b>{escape(key)}</b>: <code>{val}</code>\n"

    if parsed_url.netloc not in ["dummy.com", ""]:
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        response = f"🌐 <b>Base URL:</b>\n<code>{escape(base_url)}</code>\n\n" + response

    # Using HTML parse_mode stops Telegram from crashing on underscore '_' characters
    await update.message.reply_text(response, parse_mode="HTML")

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
