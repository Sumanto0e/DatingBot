from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def information_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    guide = InlineKeyboardButton(text=("📚 Tutorial"), callback_data="guide")
    contacts = InlineKeyboardButton(text=("📞 Kontak"), callback_data="contacts")
    language = InlineKeyboardButton(text=("🌐 language"), callback_data="language_info")
    back_to_menu = InlineKeyboardButton(
        text = ("⏪️ Kembali ke menu"), callback_data="start_menu"
    )
    markup.add(language)
    markup.row(guide, contacts)
    markup.add(back_to_menu)
    return markup
