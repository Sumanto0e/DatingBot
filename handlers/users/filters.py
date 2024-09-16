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

from functions.main_app.auxiliary_tools import (
    choice_gender,
    show_dating_filters,
)
from functions.main_app.determin_location import (
    FiltersStrategy,
    Location,
)
from handlers.users.back import (
    delete_message,
)
from keyboards.inline.change_data_profile_inline import (
    gender_keyboard,
)
from keyboards.inline.filters_inline import (
    event_filters_keyboard,
    filters_keyboard,
)
from loader import (
    dp,
)
from utils.YandexMap.exceptions import (
    NothingFound,
)
from utils.db_api import (
    db_commands,
)


@dp.callback_query_handler(text="filters")
async def get_filters(call: CallbackQuery) -> None:
    try:
        await call.message.edit_text(
            text=("Anda telah pindah ke bagian filter"),
            reply_markup=await filters_keyboard(),
        )
    except BadRequest:
        await delete_message(message=call.message)
        await call.message.answer(
            text=("Anda telah pindah ke bagian filter"),
            reply_markup=await filters_keyboard(),
        )


@dp.callback_query_handler(text="dating_filters")
async def get_dating_filters(call: CallbackQuery) -> None:
    await show_dating_filters(obj=call)


@dp.callback_query_handler(text="user_age_period")
async def desired_age(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(text=("Tulis usia minimum"))
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
    await state.finish()
    await show_dating_filters(obj=message)


@dp.callback_query_handler(text="needs_city")
async def user_city_filter(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text("Tulis kota calon pasangan Anda")
    await state.set_state("city")


@dp.callback_query_handler(text="yes_all_good", state="set_city_event")
@dp.callback_query_handler(text="yes_all_good", state="city")
async def get_hobbies(call: CallbackQuery, state: FSMContext) -> None:
    await asyncio.sleep(1)
    await call.message.edit_text("Data disimpan")
    await asyncio.sleep(2)
    if await state.get_state() == "city":
        await show_dating_filters(obj=call)
    else:
        await get_event_filters(call)

    await state.finish()


@dp.callback_query_handler(text="event_filters")
async def get_event_filters(call: CallbackQuery) -> None:
    await call.message.edit_text(
        ("Anda telah masuk ke menu pengaturan filter untuk acara"),
        reply_markup=await event_filters_keyboard(),
    )


@dp.callback_query_handler(text="city_event")
async def set_city_by_filter(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        ("Tulis kota tempat Anda ingin pergi ke suatu tempat")
    )
    await state.set_state("set_city_event")


@dp.message_handler(state="city")
async def user_city_filter_state(message: types.Message) -> None:
    try:
        loc = await Location(message=message, strategy=FiltersStrategy)
        await loc.det_loc()

    except NothingFound:
        await message.answer("Terjadi kesalahan, silakan coba lagi")
        return
