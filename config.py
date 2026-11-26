import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN در فایل .env تنظیم نشده است.")

CHANNEL_ID: str = os.getenv("CHANNEL_ID", "").strip()
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID در فایل .env تنظیم نشده است.")

CHANNEL_INVITE_LINK: str | None = os.getenv("CHANNEL_INVITE_LINK", "").strip() or None

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
DB_PATH: str = os.getenv("DB_PATH", "bot_data.db")
