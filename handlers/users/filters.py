
import asyncio
import re

from aiogram import (
    types,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)
from aiogram.utils.exceptions import (
    BadRequest,
)

from handlers.users.back import (
    delete_message,
)
from loader import (
    dp,
)
from utils.db_api import (
    db_commands,
)

@dp.callback_query_handler(text="dating_filters")
async def dating_filters(call: CallbackQuery) -> None:
    await call.message.edit_text(text=("Tulis usia minimum"))
    await delete_message(call.message)
    await state.set_state("age_period")


@dp.message_handler(state="age_period")
async def desired_min_age_state(message: types.Message, state: FSMContext) -> None:
    messages = message.text
    int_message = re.findall("[0-9]+", messages)
    int_messages = "".join(int_message)
    await db_commands.update_user_data(
        telegram_id=message.from_user.id, need_partner_age_min=int_messages
    )
    await message.answer("Sekarang masukkan usia maksimal")
    await state.reset_state()
    await state.set_state("max_age_period")


@dp.message_handler(state="max_age_period")
async def desired_max_age_state(message: types.Message, state: FSMContext) -> None:
    messages = message.text
    int_message = re.findall("[0-9]+", messages)
    int_messages = "".join(int_message)
    await db_commands.update_user_data(
        telegram_id=message.from_user.id, need_partner_age_max=int_messages
    )
    await state.town()


@dp.message_handler(state="town")
async def get_city(message: types.Message) -> None:
     try:
        censored = censored_message(message.text)
        await db_commands.update_user_data(
            need_city=quote_html(censored), telegram_id=message.from_user.id
        )
        await state.finish()
     except DataError:
        await message.answer(
            text=(
                "Telah terjadi kesalahan yang tidak diketahui! Coba ketik /start ulang kembali\n\nJika tidak bisa terus menerus lapor ke @nazhak"
            ),
            reply_markup=markup,
        )
     await state.finish()
