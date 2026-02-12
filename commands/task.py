from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from database import get_tasks, toggle_task, clear_tasks, add_task
from llm_wrapper import parse_actions

def strike(text: str) -> str:
    return ''.join(c + '\u0336' for c in text)

def build_keyboard():
    keyboard = []
    for task in get_tasks():
        text = strike(task["description"]) if task["completed"] else task["description"]
        keyboard.append([
            InlineKeyboardButton(
                f"{text}, {task['due_date']}",
                callback_data=str(task["id"])
            )
        ])
    if not keyboard:
        keyboard.append([InlineKeyboardButton("No tasks yet", callback_data="none")])
    return InlineKeyboardMarkup(keyboard)


async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Tasks:",
            reply_markup=build_keyboard()
        )
        return
    
    subcommand = context.args[0].lower()
    if subcommand == "clear":
        clear_tasks()
        await update.message.reply_text(
            "Cleared completed tasks.",
            reply_markup=build_keyboard()
        )
        return

    user_input = " ".join(context.args)
    parsed = parse_actions(user_input)
    if not parsed:
        await update.message.reply_text(
            "Could not understand the task. Try again."
        )
        return
    description = parsed["description"]
    due_date = parsed["due_date"]
    if not due_date:
        due_date = "No due date"
    add_task(description, due_date)
    await update.message.reply_text(
        f"Task added: {description} (Due: {due_date})",
        reply_markup=build_keyboard()
    )


async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        task_id = int(query.data)
    except ValueError:
        return

    toggle_task(task_id)

    await query.edit_message_reply_markup(
        reply_markup=build_keyboard()
    )


task_handler = CommandHandler("task", task)
toggle_handler = CallbackQueryHandler(toggle)
