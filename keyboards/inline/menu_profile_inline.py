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
        dating_filters = InlineKeyboardButton(
        text=("❤️ Pengaturan kenalan"), callback_data="dating_filters"
    )
    turn_off = InlineKeyboardButton(text=("🗑️ Menghapus"), callback_data="disable")
    back = InlineKeyboardButton(text=("⏪ Kembali"), callback_data="back_with_delete")
    markup.row(edit_profile, turn_off)
    markup.add(back)
    return markup

async def dating_filters_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    user_need_city = InlineKeyboardButton(
        text=("🏙️ kota pasangan anda"), callback_data="needs_city"
    )
    user_age_period = InlineKeyboardButton(
        text=("🔞Rentang usia"), callback_data="user_age_period"
    )
    user_need_gender = InlineKeyboardButton(
        text=("🚻 jenis kelamin pasangan"), callback_data="user_need_gender"
    )
    back = InlineKeyboardButton(text=("⏪️ Kembali"), callback_data="back_to_filter_menu")
    markup.add(user_need_city)
    markup.row(user_need_gender, user_age_period)
    markup.add(back)
    return markup
