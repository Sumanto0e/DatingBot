from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


async def admin_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    customers = KeyboardButton("🫂 Pengguna")
    statistik = KeyboardButton("📊 statistik")
    settings = KeyboardButton("⚙️ Pengaturan")
    advert = KeyboardButton("📊 Periklanan")
    logs = KeyboardButton("🗒 Log")
    monitoring = KeyboardButton(text="👀 Pemantauan")
    set_up_technical_works = KeyboardButton(text="🛑 Pekerjaan teknis")
    markup.add(customers, monitoring)
    markup.add(settings, statistik)
    markup.add(logs, advert)
    markup.add(set_up_technical_works)
    return markup
