import asyncio
import os
import re

from aiogram import (
    types,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
    ContentType,
)
from aiogram.utils.markdown import (
    quote_html,
)
from django.db import (
    DataError,
)

from functions.main_app.auxiliary_tools import (
    saving_censored_photo,
    update_normal_photo,
)
from functions.main_app.determin_location import (
    Location,
    RegistrationStrategy,
)
from handlers.users.back import (
    delete_message,
)
from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from loader import (
    dp,
    logger,
)
from states.new_data_state import (
    NewData,
)
from utils.db_api import (
    db_commands,
)
from utils.misc.profanityFilter import (
    censored_message,
)


@dp.callback_query_handler(text="add_inst")
async def add_inst(call: CallbackQuery, state: FSMContext) -> None:
    await delete_message(call.message)
    await call.message.answer(
        text=(
            "Tulis nama akun Anda\n\n"
            "Contoh:\n"
            "<code>@fwabase</code>\n"
            "<code>https://www.instagram.com/fwabase</code>"
        )
    )
    await state.set_state("inst")


@dp.message_handler(state="inst")
async def add_inst_state(message: types.Message, state: FSMContext) -> None:
    try:
        markup = await start_keyboard(obj=message)
        inst_regex = r"([A-Za-z0-9._](?:(?:[A-Za-z0-9._]|(?:\.(?!\.))){2,28}(?:[A-Za-z0-9._]))?)$"
        regex = re.search(inst_regex, message.text)
        result = regex
        if bool(regex):
            await state.update_data(inst=message.text)
            await db_commands.update_user_data(
                instagram=result[0], telegram_id=message.from_user.id
            )
            await message.answer(text=("Akun Anda telah berhasil ditambahkan"))
            await asyncio.sleep(1)
            await state.reset_state()
            await message.answer(
                text=("Вы были возвращены в меню"), reply_markup=markup
            )
        else:
            await message.answer(
                text=(
                    "Anda memasukkan tautan atau nama akun yang salah.\n\nContoh:\n"
                    "<code>@unknown</code>\n<code>https://www.instagram.com/unknown</code>"
                )
            )

    except DataError:
        await message.answer(text=("Telah terjadi kesalahan. coba lagi"))
        return
