import asyncio

from aiogram import (
    types,
)
from aiogram.types import (
    CallbackQuery,
    ReplyKeyboardRemove,
)

from handlers.users.back import (
    delete_message,
)
from keyboards.default.get_contact_default import (
    contact_keyboard,
)
from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from loader import (
    dp,
)
from utils.db_api import (
    db_commands,
)


@dp.callback_query_handler(text="verification")
async def get_verification_status(call: CallbackQuery) -> None:
    await delete_message(call.message)
    await call.message.answer(
        ("Untuk lulus verifikasi, Anda perlu mengirimkan kontak Anda"),
        reply_markup=await contact_keyboard(),
    )


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def get_contact(message: types.Message) -> None:
    contact = message.contact
    telegram_id = message.from_user.id
    if contact:
        await db_commands.update_user_data(verification=True, telegram_id=telegram_id)
        await db_commands.update_user_data(
            phone_number=contact.phone_number, telegram_id=telegram_id
        )
        await asyncio.sleep(2)
        await message.answer(
            text=(
                "Terima kasih, {contact_full_name}.\n"
                "Nomor Anda {contact_phone_number} telah diterima."
            ).format(
                contact_full_name=contact.full_name,
                contact_phone_number=contact.phone_number,
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
        await asyncio.sleep(4)
        await delete_message(message)
        await message.answer(
            ("Anda telah dikembalikan ke menu"),
            reply_markup=await start_keyboard(obj=message),
        )
    else:
        await db_commands.update_user_data(verification=False, telegram_id=telegram_id)
        await message.answer("Nomor Anda tidak valid, silakan coba lagi.")
