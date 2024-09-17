from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

async def filters_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    event_filters = InlineKeyboardButton(
        text=("🎉 Acara"), callback_data="event_filters"
    )
    dating_filters = InlineKeyboardButton(
        text=("❤️ Kenalan"), callback_data="dating_filters"
    )
    back = InlineKeyboardButton(text=_("⏪️ Назад"), callback_data="back_with_delete")
    markup.row(event_filters, dating_filters)
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


async def event_filters_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    city_event = InlineKeyboardButton(text=("🏙️ Kota"), callback_data="city_event")
    back = InlineKeyboardButton(
        text=("⏪️ Kembali ke menu"), callback_data="back_to_filter_menu"
    )
    markup.add(city_event)
    markup.add(back)
    return markup
