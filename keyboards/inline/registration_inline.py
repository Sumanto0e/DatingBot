from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def second_registration_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    questionnaire = InlineKeyboardButton(
        text= ("🖌️ Registrasi"), callback_data="survey"
    )
    back_to_menu = InlineKeyboardButton(
        text= ("⏪️ Kembali ke menu"), callback_data="start_menu"
    )
    markup.add(questionnaire, back_to_menu)
    return markup


async def confirm_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    yes_all_good = InlineKeyboardButton(
        text= ("✅ Ya semuanya baik-baik saja!"), callback_data="yes_all_good"
    )
    markup.add(yes_all_good)
    return markup
