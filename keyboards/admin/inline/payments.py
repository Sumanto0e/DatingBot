from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def payments_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    settings = InlineKeyboardButton(
        ("⚙️ Pengaturan"), callback_data="payments:settings"
    )
    statistics = InlineKeyboardButton(("📝 Statistik"), callback_data="payments:stats")
    markup.add(statistics, settings)
    return markup
