from typing import (
    Union,
)

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from data.config import (
    load_config,
)
from utils.db_api import (
    db_commands,
)


async def start_keyboard(
        obj: Union[CallbackQuery, Message, int]
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    try:
        user_db = await db_commands.select_user(telegram_id=obj.from_user.id)
    except AttributeError:
        user_db = await db_commands.select_user(telegram_id=obj)
    status = user_db.status
    support_ids = load_config().tg_bot.support_ids[0]
    registration = InlineKeyboardButton(
        text=("➕ Pendaftaran"), callback_data="registration"
    )
    language = InlineKeyboardButton(text=("🌐 language"), callback_data="language_reg")
    my_profile = InlineKeyboardButton(
        text=("👤 Profil"), callback_data="my_profile"
    )
    view_ques = InlineKeyboardButton(text=("💌 Temukan pasangan"), callback_data="find_ques")
    support = InlineKeyboardButton(text=("Tutorial"), url="https://vt.tiktok.com/ZS2qAL22x/")
    information = InlineKeyboardButton(
        text=("ℹ️ Informasi"), callback_data="information"
    )
    if not status:
        markup.row(registration)
        markup.row(support, information)
        markup.row(language)
    else:
        markup.row(my_profile, information)
        markup.row(view_ques)
        try:
            if support_ids != obj.from_user.id:
                markup.row(support)
        except AttributeError:
            if support_ids != obj:
                markup.row(support)
    return markup
