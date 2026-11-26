"""
لایه دسترسی به API رسمی بله.
فقط از endpointهای واقعی استفاده می‌کند.
"""
import logging
from bale import Bot
from config import CHANNEL_ID, CHANNEL_INVITE_LINK

logger = logging.getLogger(__name__)


async def get_channel_invite_link(bot: Bot) -> str | None:
    """
    دریافت لینک دعوت کانال.
    اولویت با CHANNEL_INVITE_LINK در .env است.
    در غیر این صورت از export_chat_invite_link استفاده می‌شود.
    """
    if CHANNEL_INVITE_LINK:
        return CHANNEL_INVITE_LINK

    try:
        link = await bot.export_chat_invite_link(CHANNEL_ID)
        return link
    except Exception as e:
        logger.error("خطا در دریافت لینک دعوت کانال: %s", e)
        return None
