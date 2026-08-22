import logging
from urllib.parse import parse_qs, urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Mujhe koi bhi URL bhejiye, main usme se sare parameters "
        "(jaise aff_id, click_id, etc.) alag karke de dunga."
    )

# URL parameters extract karne ka function
async def extract_parameters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    # URL parse karein
    parsed_url = urlparse(user_text)
    if not parsed_url.scheme or not parsed_url.netloc:
        query_string = user_text if "?" in user_text else f"?{user_text}"
        parsed_url = urlparse(f"http://dummy.com/{query_string}")

    query_params = parse_qs(parsed_url.query)

    if not query_params:
        await update.message.reply_text("❌ Is URL ya text mein koi bhi parameters nahi mile.")
        return

    # Response format karein
    response = "🔍 **Extracted Parameters:**\n\n"
    for key, values in query_params.items():
        response += f"• **{key}**: `{values[0]}`\n"

    if parsed_url.netloc != "dummy.com" and parsed_url.netloc != "":
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        response = f"🌐 **Base URL:**\n`{base_url}`\n\n" + response

    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    # Aapka Bot Token yahan set hai
    TOKEN = "8761704094:AAHYOLC_IRlct6YukFPYtTJlRZRmNCfEDGI"

    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), extract_parameters))

    print("🤖 Bot start ho gaya hai aur live hai...")
    application.run_polling()

if __name__ == "__main__":
    main()
