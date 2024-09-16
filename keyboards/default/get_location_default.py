from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


async def location_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    send_location = KeyboardButton(
        text=_("🗺 Kirim lokasi secara otomatis"), request_location=True
    )
    markup.add(send_location)
    return markup
