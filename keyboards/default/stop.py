from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

async def stop_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    first_button = KeyboardButton(text=("💤 Berhenti"), request_stop=True)
    markup.add(first_button)
    return markup
