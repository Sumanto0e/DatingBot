from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def language_keyboard(menu: str) -> InlineKeyboardMarkup:
    menu_back_buttons = {
        "registration": "back_to_reg_menu",
        "information": "back_to_info_menu",
    }

    markup = InlineKeyboardMarkup()
    ru = InlineKeyboardButton(text=("🇷🇺 Rusia"), callback_data="Russian")
    de = InlineKeyboardButton(text=("🇩🇪 Jerman"), callback_data="Deutsch")
    eng = InlineKeyboardButton(text=("🇬🇧 Inggris"), callback_data="English")
    ind = InlineKeyboardButton(text=("🇮🇩 Indonesia"), callback_data="Indonesian")
    markup.row(ru, de)
    markup.row(eng, ind)
    back_button = menu_back_buttons.get(menu)
    if back_button:
        back = InlineKeyboardButton(
            text=("⏪️ Kembali ke menu"), callback_data=back_button
        )
        markup.add(back)
    return markup
