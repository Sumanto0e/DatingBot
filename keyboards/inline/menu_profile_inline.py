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
        text=("🖊 Pengaturan akun"), callback_data="change_profile"
    )
    add_instagram = InlineKeyboardButton(
        text=("📸 Pengaturan Sosmed"), callback_data="add_inst"
    )
    dating_filters = InlineKeyboardButton(text=("❤️ Pengaturan kenalan"), callback_data="dating_filters")
    turn_off = InlineKeyboardButton(text=("🗑️ Menghapus"), callback_data="disable")
    back = InlineKeyboardButton(text=("⏪ Kembali"), callback_data="back_with_delete")
    markup.row(edit_profile, add_instagram)
    markup.row(turn_off, dating_filters)
    markup.add(back)
    return markup

async def gender_keyboard(m_gender: str, f_gender: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    male = InlineKeyboardButton(text=m_gender, callback_data="male")
    female = InlineKeyboardButton(text=f_gender, callback_data="female")
    stopped = InlineKeyboardButton(
        text=("❌ Berhenti"), callback_data="registration:stopped"
    )
    markup.row(male, female)
    markup.add(stopped)
    return markup
