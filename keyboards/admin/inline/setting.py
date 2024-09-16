from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def add_admins_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    add = InlineKeyboardButton(_("*️⃣ Menambahkan"), callback_data="admin:admins:add")
    delete = InlineKeyboardButton(_("❌ Menghapus"), callback_data="admin:admins:delete")
    back = InlineKeyboardButton(_("◀️ Kembali"), callback_data="admin:settings")
    markup.add(add, delete)
    markup.add(back)
    return markup
