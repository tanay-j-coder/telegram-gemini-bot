
import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME")  # without @

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API function
def ask_gemini(question):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [{"parts": [{"text": question}]}]
        }
        response = requests.post(url, headers=headers, json=body)
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        return "Sorry, Gemini couldn't respond right now."

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm Gemini AI. Tag me in a group or talk to me directly!")

# Message handler for both private and group chats
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    if message.chat.type == "private":
        question = message.text
    else:
        # Only respond in group if the bot is mentioned
        entities = message.entities or []
        mentioned = any(
            e.type == "mention" and BOT_USERNAME.lower() in message.text[e.offset:e.offset + e.length].lower()
            for e in entities
        )
        if not mentioned:
            return
        question = message.text

    reply = ask_gemini(question)
    await message.reply_text(reply)

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Update {update} caused error {context.error}")

# Main bot entry
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("✅ Gemini Group Bot is running...")
    app.run_polling()
