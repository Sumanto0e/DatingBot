from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def cancel_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    cancel = InlineKeyboardButton(text=_("Отмена"), callback_data="cancel")
    markup.add(cancel)
    return markup


async def cancel_registration_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    stopped = InlineKeyboardButton(
        text= ("❌ Остановить"), callback_data="registration:stopped"
    )
    markup.add(stopped)
    return markup
