from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


async def admin_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    mailing = KeyboardButton(text=("broadcast"))
    message_by_id = KeyboardButton(text=("Pesan oleh id"))
    count_people_and_chat = KeyboardButton(text=("Hitung orang dan obrolan"))
    monitoring = KeyboardButton(text=("Pemantauan"))
    set_up_technical_works = KeyboardButton(text=("Pekerja teknis"))
    markup.row(mailing, message_by_id)
    markup.row(count_people_and_chat, monitoring)
    markup.add(set_up_technical_works)
    return markup
