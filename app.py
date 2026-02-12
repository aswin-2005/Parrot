import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from commands.start import start_handler
from commands.task import task_handler, toggle_handler
from llm_wrapper import chat

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://yourdomain.com

# ------------------------
# FASTAPI APP
# ------------------------

app = FastAPI()

# ------------------------
# TELEGRAM APPLICATION
# ------------------------

telegram_app: Application = ApplicationBuilder().token(BOT_TOKEN).build()


# ------------------------
# TELEGRAM HANDLERS
# ------------------------

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = chat(user_input)
    await update.message.reply_text(response)


telegram_app.add_handler(start_handler)
telegram_app.add_handler(task_handler)
telegram_app.add_handler(toggle_handler)
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler)
)


# ------------------------
# HEALTH ENDPOINT (FOR CRON)
# ------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


# ------------------------
# TELEGRAM WEBHOOK ENDPOINT
# ------------------------

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# ------------------------
# STARTUP EVENT
# ------------------------

@app.on_event("startup")
async def on_startup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print("Webhook set successfully")


# ------------------------
# SHUTDOWN EVENT
# ------------------------

@app.on_event("shutdown")
async def on_shutdown():
    await telegram_app.shutdown()
