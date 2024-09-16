from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


async def get_photo_from_profile() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    send_photo = KeyboardButton(text=("Ambil dari profil"))
    markup.add(send_photo)
    return markup
