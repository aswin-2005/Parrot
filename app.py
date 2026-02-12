from telegram.ext import ApplicationBuilder, MessageHandler, filters
from dotenv import load_dotenv
import os

from commands.start import start_handler
from commands.task import task_handler, toggle_handler
from llm_wrapper  import chat

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

from telegram import Update
from telegram.ext import ContextTypes

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = chat(user_input)
    await update.message.reply_text(response)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(start_handler)
    app.add_handler(task_handler)
    app.add_handler(toggle_handler)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("Bot is running...")

    app.run_polling()

if __name__ == "__main__":
    main()
