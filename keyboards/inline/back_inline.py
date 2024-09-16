from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def only_back_keyboard(menu: str = "start_menu") -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton(text=("⏪️ Kembali ke menu"), callback_data=menu)
    markup.add(back)
    return markup
