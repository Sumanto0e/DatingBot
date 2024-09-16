from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def cancel_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    cancel = InlineKeyboardButton(text=("Membatalkan"), callback_data="cancel")
    markup.add(cancel)
    return markup


async def cancel_registration_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    stopped = InlineKeyboardButton(
        text= ("❌ Berhenti"), callback_data="registration:stopped"
    )
    markup.add(stopped)
    return markup
