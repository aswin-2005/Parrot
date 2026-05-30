import os
import html
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Initialize Configuration from Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_SECRET_TOKEN = os.environ.get("API_SECRET_TOKEN")

app = FastAPI(title="Parrot API Server")
bot = Bot(token=TELEGRAM_BOT_TOKEN)
security_scheme = HTTPBearer()

class NotificationPayload(BaseModel):
    sender: str = Field(..., example="Backup Script")
    message: str = Field(..., example="Database synced successfully.")
    level: str = Field(default="info", example="info")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    if credentials.credentials != API_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
        )
    return credentials.credentials

# Maps level name → (emoji, display label)
_LEVEL_CONFIG: dict[str, tuple[str, str]] = {
    "success": ("🟢", "SUCCESS"),
    "info":    ("🔵", "INFO"),
    "warning": ("🟡", "WARNING"),
    "error":   ("🔴", "ERROR"),
}

def get_level_config(level: str) -> tuple[str, str]:
    """Return (emoji, LABEL) for a given level string."""
    return _LEVEL_CONFIG.get(level.lower().strip(), ("▪️", level.upper()))

# The Post Route
@app.post("/send", status_code=status.HTTP_200_OK)
async def send_notification(payload: NotificationPayload, token: str = Depends(verify_token)):
    # Full day, date, and time string
    full_timestamp = datetime.now().strftime("%A, %B %d, %Y  •  %I:%M %p")

    emoji, label = get_level_config(payload.level)

    # Escape all user-controlled strings before injecting into HTML
    sender_clean  = html.escape(payload.sender)
    message_clean = html.escape(payload.message)
    time_clean    = html.escape(full_timestamp)

    # Layout Strategy:
    # • Dot emoji alone signals the level — no redundant text label needed.
    # • Sender is bold and prominent — the first thing you read.
    # • Message body gets its own paragraph with breathing room.
    # • Timestamp is italic at the bottom — subtle, secondary, out of the way.
    formatted_msg = (
        f"{emoji}  <b>{sender_clean}</b>\n\n"
        f"{message_clean}\n\n"
        f"<i>{time_clean}</i>"
    )
    
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=formatted_msg,
            parse_mode="HTML",
            disable_web_page_preview=True  # Stops Telegram from trying to preview the dead link
        )
        return {"status": "success", "detail": "Parrot accepted your message"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parrot failed to deliver message: {str(e)}"
        )