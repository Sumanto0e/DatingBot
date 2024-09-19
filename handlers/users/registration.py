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
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.markdown import (
    quote_html,
)
from asyncpg import (
    UniqueViolationError,
)
from django.db import (
    DataError,
)
from handlers.users.back import (
    delete_message,
)
from functions.main_app.auxiliary_tools import (
    choice_gender,
    saving_censored_photo,
    saving_normal_photo,
)
from keyboards.inline.menu_profile_inline import (
    gender_keyboard,
    get_profile_keyboard,
)
from keyboards.default.get_photo import (
    get_photo_from_profile,
)
from keyboards.inline.cancel_inline import (
    cancel_registration_keyboard,
)
from loader import (
    bot,
    dp,
    logger,
)
from states.reg_state import (
    RegData,
)
from utils.NudeNet.predictor import (
    classification_image,
    generate_censored_image,
)
from utils.db_api import (
    db_commands,
)
from utils.misc.profanityFilter import (
    censored_message,
)


@dp.callback_query_handler(text_contains="registration")
async def survey(call: CallbackQuery) -> None:
    markup = await gender_keyboard(
        m_gender=("👱🏻‍♂️ male"), f_gender=("👱🏻‍♀️ female")
    )

    await call.message.edit_text(("Pilih jenis kelamin"), reply_markup=markup)
    await RegData.sex.set()


@dp.callback_query_handler(state=RegData.sex)
async def sex_reg(call: CallbackQuery) -> None:
    if call.data == "male":
        try:
            await db_commands.update_user_data(
                telegram_id=call.from_user.id, sex="male"
            )
            await db_commands.update_user_data(
                telegram_id=call.from_user.id, need_partner_sex="female"
            )
        except UniqueViolationError:
            pass
    elif call.data == "female":
        try:
            await db_commands.update_user_data(
                telegram_id=call.from_user.id, need_partner_sex="female"
            )
            await db_commands.update_user_data(
                telegram_id=call.from_user.id, need_partner_sex="male"
            )
        except UniqueViolationError:
            pass

    await call.message.edit_text(
        text=("Status profil anda?"),
    )
    await RegData.commentary.set()


@dp.message_handler(content_types=[ContentType.TEXT], state=RegData.commentary)
async def commentary_reg(message: types.Message) -> None:
    try:
        censored = censored_message(message.text)
        await db_commands.update_user_data(
            commentary=quote_html(censored), telegram_id=message.from_user.id
        )
        await message.answer(
            text=("Masukan nama anda: ")
        )

    except DataError:
        await message.answer(
            text=(
                "Telah terjadi kesalahan yang tidak diketahui! Coba ubah komentar nanti di bagian tersebut"
                '"Menu"\n\n'
                "Masukan nama anda: "
            ),
            reply_markup=markup,
        )
    await RegData.name.set()


@dp.message_handler(state=RegData.name)
async def get_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    censored = censored_message(message.text)
    await db_commands.update_user_data(
        telegram_id=message.from_user.id, varname=quote_html(censored)
    )
    await message.answer(text=("Berapa umur Anda?"))
    await state.reset_state()
    await RegData.age.set()


# TODO: Убрать возможность у пользователя использовать ввод для определения города
@dp.message_handler(state=RegData.age)
async def get_age(message: types.Message, state: FSMContext) -> None:
    messages = message.text
    int_message = re.findall("[0-9]+", messages)
    int_messages = "".join(int_message)
    await db_commands.update_user_data(
        telegram_id=message.from_user.id, need_partner_age_max=int_messages
    )
    await message.answer(
        text=("Di kota mana anda tinggal?"),
    )
    await state.reset_state()
    await RegData.town.set()
    

@dp.message_handler(state=RegData.town)
async def get_city(message: types.Message) -> None:
     try:
        censored = censored_message(message.text)
        await db_commands.update_user_data(
            city=quote_html(censored), telegram_id=message.from_user.id
        )
        await db_commands.update_user_data(
            need_city=quote_html(censored), telegram_id=message.from_user.id
        )
        await message.answer(
        text=(
            "Dan terakhir, kirimkan saya foto Anda"
            " (Anda perlu mengirim gambar terkompresi, bukan dengan bentuk dokumen)"
        ),
        reply_markup=await get_photo_from_profile(),
        )
        await RegData.photo.set()
     except DataError:
        await message.answer(
            text=(
                "Telah terjadi kesalahan yang tidak diketahui! Coba ubah komentar nanti di bagian tersebut"
                '"Menu"\n\n'
                "Masukan nama anda: "
            ),
            reply_markup=markup,
        )

@dp.callback_query_handler(text="yes_all_good", state=RegData.town)
async def get_hobbies(call: CallbackQuery) -> None:
    await call.message.delete()
    await call.message.answer(
        text=(
            "Dan terakhir, kirimkan saya foto Anda"
            " (Anda perlu mengirim gambar terkompresi, bukan dengan bentuk dokumen)"
        ),
        reply_markup=await get_photo_from_profile(),
    )
    await RegData.photo.set()


@dp.message_handler(state=RegData.photo)
async def get_photo_profile(message: types.Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    profile_pictures = await dp.bot.get_user_profile_photos(telegram_id)
    try:
        file_id = dict((profile_pictures.photos[0][0])).get("file_id")
        await saving_normal_photo(
            message=message, telegram_id=telegram_id, file_id=file_id, state=state
        )
    except IndexError:
        await message.answer(
            text=("Terjadi kesalahan, silakan periksa pengaturan privasi Anda"),
            reply_markup=await cancel_registration_keyboard(),
        )


@dp.message_handler(content_types=ContentType.PHOTO, state=RegData.photo)
async def get_photo(message: types.Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    file_name = f"{str(telegram_id)}.jpg"
    file_id = message.photo[-1].file_id
    censored_file_name = f"{str(message.from_user.id)}_censored.jpg"
    path = f"photos/{file_name}"
    out_path = f"photos/{censored_file_name}"
    await message.photo[-1].download(path)
    data = await classification_image(path)

    exposed_labels = [
        "FEMALE_GENITALIA_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
        "FEMALE_BREAST_EXPOSED",
    ]
    if any(item["class"] in exposed_labels for item in data):
        await generate_censored_image(image_path=path, out_path=out_path)
        await saving_censored_photo(
            message=message, telegram_id=telegram_id, state=state, out_path=out_path
        )
        os.remove(path)
        os.remove(out_path)
    else:
        await saving_normal_photo(
            message=message, telegram_id=telegram_id, file_id=file_id, state=state
        )
        os.remove(path)

@dp.callback_query_handler(text="change_profile")
async def start_change_data(call: CallbackQuery) -> None:
    markup = await gender_keyboard(
        m_gender=("👱🏻‍♂️ male"), f_gender=("👱🏻‍♀️ female")
    )
    await delete_message(call.message)
    await call.message.answer(text=("<u>Pilih jenis kelamin: </u>\n"), reply_markup=markup)
    await RegData.sex.set()


@dp.callback_query_handler(text="dating_filters")
async def get_filters(call: CallbackQuery, state: FSMContext) -> None:
    await delete_message(call.message)
    await call.message.answer(
        text=("Usia minimal pasangan anda"),
    )
    await state.set_state("max_age_period")

@dp.message_handler(state="max_age_period")
async def desired_max_age_state(message: types.Message, state: FSMContext) -> None:
    messages = message.text
    int_message = re.findall("[0-9]+", messages)
    int_messages = "".join(int_message)
    await db_commands.update_user_data(
        telegram_id=message.from_user.id, need_partner_age_min=int_messages
    )
    await message.answer(
        text=("Usia maksimal pasangan anda"),
    )
    await state.reset_state()
    await state.set_state("town")
    
@dp.message_handler(state="town")
async def get_city(message: types.Message, state: FSMContext) -> None:
    messages = message.text
    int_message = re.findall("[0-9]+", messages)
    int_messages = "".join(int_message)
    await db_commands.update_user_data(
    telegram_id=message.from_user.id, need_partner_age_max=int_messages
    )
    await message.answer(
        text=("Kota pasangan anda"),
    )
    await state.reset_state()
    await state.set_state("finish_data")
    
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
        inst_regex = r"([A-Za-z0-9._](?:(?:[A-Za-z0-9._]|(?:\.(?!\.))){2,28}(?:[A-Za-z0-9._]))?)$"
        regex = re.search(inst_regex, message.text)
        result = regex
        if bool(regex):
            await state.update_data(inst=message.text)
            await db_commands.update_user_data(
                instagram=result[0], telegram_id=message.from_user.id
            )
            await message.answer(text=("Akun Anda telah berhasil ditambahkan"))
            await state.reset_state()
            await state.set_state("finish_data")
            
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

@dp.message_handler(state="finish_data")
async def finish_filter(message: types.Message, state: FSMContext) -> None:
    censored = censored_message(message.text)
    await db_commands.update_user_data(
        need_city=quote_html(censored), telegram_id=message.from_user.id
    )
    await state.finish()
    user = await db_commands.select_user(telegram_id=message.from_user.id)
    user_verification = "✅" if user.verification else ""
    user_info_template = (
        "{name}, {age} tahun, {city}, {verification}\n\n{commentary}\n\n"
        "Filter pasangan anda:\n\n"
        "🚻 lawan jenis anda: {need_partner_sex}\n"
        "🔞 Rentang usia: {min}-{max} tahun\n"
        "🏙️ kota: {need_city}"
    )
    info = await bot.get_me()
    user_info = user_info_template.format(
        name=user.varname,
        age=user.age,
        city=user.city,
        verification=user_verification,
        commentary=user.commentary,
        need_partner_sex=user.need_partner_sex,
        min=user.need_partner_age_min,
        max=user.need_partner_age_max,
        need_city=user.need_city,
    )
    markup = InlineKeyboardMarkup(row_width=2)
    edit_profile = InlineKeyboardButton(
        text=("🖊 Pengaturan akun"), callback_data="change_profile"
    )
    dating_filters = InlineKeyboardButton(text=("❤️ Pengaturan kenalan"), callback_data="dating_filters")
    turn_off = InlineKeyboardButton(text=("🗑️ Menghapus"), callback_data="disable")
    back = InlineKeyboardButton(text=("⏪ Kembali"), callback_data="back_with_delete")
    markup.row(edit_profile)
    markup.row(turn_off, dating_filters)
    markup.add(back)
    await message.answer_photo(
        caption=user_info, photo=user.photo_id, reply_markup=markup
    )

