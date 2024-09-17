from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def add_admins_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    add = InlineKeyboardButton(("*️⃣ Menambahkan"), callback_data="admin:admins:add")
    delete = InlineKeyboardButton(("❌ Menghapus"), callback_data="admin:admins:delete")
    back = InlineKeyboardButton(("◀️ Kembali"), callback_data="admin:settings")
    markup.add(add, delete)
    markup.add(back)
    return markup
