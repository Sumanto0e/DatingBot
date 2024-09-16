from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

async def get_profile_keyboard(verification) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    if not verification:
        verification_btn = InlineKeyboardButton(
            text=("✅ Verifikasi"), callback_data="verification"
        )
        markup.row(verification_btn)
    edit_profile = InlineKeyboardButton(
        text=("🖊 Setting akun"), callback_data="change_profile"
    )
    turn_off = InlineKeyboardButton(text=("🗑️ Menghapus"), callback_data="disable")
    back = InlineKeyboardButton(text=("⏪ Kembali"), callback_data="back_with_delete")
    markup.row(edit_profile, turn_off)
    markup.add(back)
    return markup
