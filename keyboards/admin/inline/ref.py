from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

async def referral_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    statistics = InlineKeyboardButton(("📈 Statistik"), callback_data="ref_urls:stats")
    add_ref = InlineKeyboardButton(("*️⃣ Menambahkan"), callback_data="ref_urls:create")
    delete_ref = InlineKeyboardButton(("❌ Menghapus"), callback_data="ref_urls:delete")
    back = InlineKeyboardButton(("◀️ Kembali"), callback_data="admin:mailing_md")
    markup.add(statistics, add_ref, delete_ref, back)
    return markup
