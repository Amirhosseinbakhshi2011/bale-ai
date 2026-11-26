import logging
from bale import Bot, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import config
from database import (
    init_db,
    add_or_update_start,
    mark_consent,
    mark_invite_sent,
    has_consented,
    log_action,
)
from baale_api import get_channel_invite_link

# -------------------- Logging --------------------
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("BaaleJoinBot")

# -------------------- Bot Instance --------------------
bot = Bot(token=config.BOT_TOKEN)


# -------------------- Events --------------------

@bot.event
async def on_ready():
    await init_db()
    me = bot.user
    logger.info("ربات آماده است | نام: %s | آیدی: %s", me.username, me.user_id)


@bot.event
async def on_message(message: Message):
    if not message.content:
        return

    text = message.content.strip()

    if text == "/start":
        user = message.from_user or getattr(message, "author", None)
        if not user:
            return

        user_id = getattr(user, "user_id", None) or getattr(user, "id", None)
        username = getattr(user, "username", None)
        first_name = getattr(user, "first_name", None) or "کاربر"

        await add_or_update_start(user_id, username, first_name)
        await log_action(user_id, "start", f"username={username}")

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="✅ عضویت در کانال", callback_data="consent_join"))

        reply_text = (
            f"سلام {first_name} 👋\n\n"
            "به ربات مدیریت عضویت کانال خوش آمدید.\n\n"
            "برای عضویت در کانال، لطفاً روی لینک زیر کلیک کنید.\n\n"
            "ble.ir/daneshneshan\n"
	    	       
        )

        await message.reply(reply_text, components=keyboard)
        logger.info("کاربر %s استارت زد", user_id)


@bot.event
async def on_callback_query(callback: CallbackQuery):
    if callback.data != "consent_join":
        return

    user = callback.from_user
    if not user:
        await callback.answer("خطا در شناسایی کاربر", show_alert=True)
        return

    user_id = getattr(user, "user_id", None) or getattr(user, "id", None)
    first_name = getattr(user, "first_name", None) or "کاربر"

    # جلوگیری از ارسال مکرر
    if await has_consented(user_id):
        await callback.answer("قبلاً لینک دعوت برای شما ارسال شده است.", show_alert=True)
        return

    await mark_consent(user_id)
    await log_action(user_id, "consent", "کاربر رضایت عضویت را اعلام کرد")

    invite_link = await get_channel_invite_link(bot)

    if not invite_link:
        await callback.answer(
            "متأسفانه در حال حاضر لینک دعوت در دسترس نیست. لطفاً بعداً تلاش کنید.",
            show_alert=True
        )
        await log_action(user_id, "error", "لینک دعوت دریافت نشد")
        logger.error("لینک دعوت برای کاربر %s دریافت نشد", user_id)
        return

    await mark_invite_sent(user_id)
    await log_action(user_id, "invite_sent", invite_link)

    text = (
        f"{first_name} عزیز،\n\n"
        "از اعلام رضایت شما متشکریم.\n"
        "برای عضویت در کانال روی لینک زیر کلیک کنید:\n\n"
        f"🔗 {invite_link}\n\n"
        "بعد از ورود به کانال، پیام خوش‌آمدگویی دریافت خواهید کرد."
    )

    try:
        if callback.message:
            await callback.message.reply(text)
        await callback.answer("لینک دعوت ارسال شد ✅")
    except Exception as e:
        logger.exception("خطا در ارسال پیام به کاربر %s: %s", user_id, e)
        await log_action(user_id, "error", str(e))
        await callback.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", show_alert=True)


# -------------------- Run --------------------

if __name__ == "__main__":
    logger.info("در حال راه‌اندازی ربات...")
    bot.run()
