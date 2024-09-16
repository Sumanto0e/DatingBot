from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def mailing_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    mailing = InlineKeyboardButton(("📧 Broadcast"), callback_data="adv:mailing")
    markup.add(mailing)
    return markup


async def add_buttons_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    confirm_sending = InlineKeyboardButton(
        text=_("Konfirmasikan pengiriman"), callback_data="confirm_send"
    )
    add_button = InlineKeyboardButton(
        text=("Tambahkan tombol"), callback_data="add_buttons"
    )
    cancel = InlineKeyboardButton(text=("Membatalkan"), callback_data="cancel")

    markup.row(confirm_sending, add_button)
    markup.add(cancel)
    return markup


async def confirm_with_button_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    confirm_sending = InlineKeyboardButton(
        text=("Konfirmasikan pengiriman"), callback_data="confirm_send_with_button"
    )
    cancel = InlineKeyboardButton(text=("Membatalkan"), callback_data="cancel")
    markup.add(confirm_sending)
    markup.add(cancel)
    return markup
