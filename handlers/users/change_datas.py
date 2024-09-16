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
from keyboards.default.get_photo import (
    get_photo_from_profile,
)
from keyboards.inline.change_data_profile_inline import (
    change_info_keyboard,
    gender_keyboard,
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
from utils.NudeNet.predictor import (
    classification_image,
    generate_censored_image,
)
from utils.YandexMap.exceptions import (
    NothingFound,
)
from utils.db_api import (
    db_commands,
)
from utils.misc.profanityFilter import (
    censored_message,
)


@dp.callback_query_handler(text="change_profile")
async def start_change_data(call: CallbackQuery) -> None:
    markup = await change_info_keyboard()
    await delete_message(call.message)
    await call.message.answer(text=_("<u>Data Anda: </u>\n"), reply_markup=markup)


@dp.callback_query_handler(text="name")
async def change_name_request(call: CallbackQuery) -> None:
    await call.message.edit_text(text=("Masukkan nama baru"))
    await NewData.name.set()


@dp.message_handler(state=NewData.name)
async def update_name(message: types.Message, state: FSMContext) -> None:
    markup = await change_info_keyboard()
    try:
        censored = censored_message(message.text)
        await db_commands.update_user_data(
            varname=quote_html(censored), telegram_id=message.from_user.id
        )
        await message.answer(
            text=(
                "Nama barumu: <b>{censored}</b>\n"
                "Pilih apa yang ingin Anda ubah: "
            ).format(censored=censored),
            reply_markup=markup,
        )
        await state.reset_state()
    except DataError as ex:
        logger.error(f"Error in change_name: {ex}")
        await message.answer(
            text=(
                "Telah terjadi kesalahan yang tidak diketahui. Coba lagi\n"
                "Mungkin pesan Anda terlalu besar"
            ),
            reply_markup=markup,
        )
        return

    await state.reset_state()


@dp.callback_query_handler(text="age")
async def change_age(call: CallbackQuery) -> None:
    await call.message.edit_text(text=("Masuki zaman baru"))
    await NewData.age.set()


@dp.message_handler(state=NewData.age)
async def update_age(message: types.Message, state: FSMContext) -> None:
    markup = await change_info_keyboard()
    try:
        if int(message.text) and 10 < int(message.text) < 90:
            await db_commands.update_user_data(
                age=int(message.text), telegram_id=message.from_user.id
            )
            await asyncio.sleep(1)
            await message.answer(
                text=(
                    "Usia anda: <b>{messages}</b>\n"
                    "Memilih, apa yang ingin kamu ubah: "
                ).format(messages=message.text),
                reply_markup=markup,
            )
            await state.reset_state()
        else:
            await message.answer(
                text=("Nomor yang Anda masukkan tidak valid, silakan coba lagi")
            )
            return

    except ValueError:
        await message.answer(text=("Anda salah memasukkan nomor, silakan coba lagi"))
        return

    await state.reset_state()


@dp.callback_query_handler(text="city")
async def change_city(call: CallbackQuery) -> None:
    await call.message.edit_text(text=("Masuki kota anda"))
    await NewData.city.set()


@dp.message_handler(state=NewData.city)
async def update_city(message: types.Message) -> None:
    try:
        loc = await Location(message=message, strategy=RegistrationStrategy())
        await loc.det_loc()
    except NothingFound as ex:
        logger.error(f"Error in change_city. {ex}")
        await message.answer(
            text=("Kami tidak dapat menemukan kota itu {city}. Coba lagi").format(
                city=message.text
            )
        )
        return


@dp.callback_query_handler(text="yes_all_good", state=NewData.city)
async def get_hobbies(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        text=("Data telah berhasil diubah.\n" "Pilih apa yang ingin Anda ubah: "),
        reply_markup=await change_info_keyboard(),
    )
    await state.reset_state()


@dp.callback_query_handler(text="gender")
async def change_sex(call: CallbackQuery) -> None:
    markup = await gender_keyboard(
        m_gender=("👱🏻‍♂️ male"), f_gender=_("👱🏻‍♀️ female")
    )
    await call.message.edit_text(text=("Pilih gender anda: "), reply_markup=markup)
    await NewData.sex.set()


@dp.callback_query_handler(state=NewData.sex)
async def update_sex(call: CallbackQuery, state: FSMContext) -> None:
    markup = await change_info_keyboard()
    gender = "male" if call.data == "male" else "female"
    need_gender = "male" if call.data == "female" 
    await db_commands.update_user_data(sex=gender, telegram_id=call.from_user.id)
    await db_commands.update_user_data(sex=need_gender, telegram_id=call.from_user.id)
    await call.message.edit_text(
        text=(
            "Gender Anda: <b>{}</b>\n" "Memilih, apa yang ingin kamu ubah: "
        ).format(gender),
        reply_markup=markup,
    )
    await state.reset_state()


@dp.callback_query_handler(text="photo")
async def new_photo(call: CallbackQuery) -> None:
    await delete_message(call.message)
    await call.message.answer(
        text=_("Отправьте мне новую фотографию"),
        reply_markup=await get_photo_from_profile(),
    )
    await NewData.photo.set()
    await asyncio.sleep(1)
    await delete_message(call.message)


@dp.message_handler(state=NewData.photo)
async def get_photo_profile(message: types.Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    markup = await change_info_keyboard()
    profile_pictures = await dp.bot.get_user_profile_photos(telegram_id)
    try:
        file_id = dict((profile_pictures.photos[0][0])).get("file_id")
        await update_normal_photo(
            message=message,
            telegram_id=telegram_id,
            file_id=file_id,
            state=state,
            markup=markup,
        )
    except IndexError:
        await message.answer(
            text=("Terjadi kesalahan, silakan periksa pengaturan privasi Anda")
        )


@dp.message_handler(content_types=ContentType.PHOTO, state=NewData.photo)
async def update_photo_complete(message: types.Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    markup = await change_info_keyboard()
    file_name = f"{str(telegram_id)}.jpg"
    file_id = message.photo[-1].file_id
    censored_file_name = f"{str(message.from_user.id)}_censored.jpg"
    path, out_path = f"photos/{file_name}", f"photos/{censored_file_name}"

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
            message=message,
            telegram_id=telegram_id,
            state=state,
            out_path=out_path,
            markup=markup,
            flag="change_datas",
        )
        os.remove(path)
        await asyncio.sleep(0.2)
        os.remove(out_path)
    else:
        await update_normal_photo(
            message=message,
            telegram_id=telegram_id,
            file_id=file_id,
            state=state,
            markup=markup,
        )
        os.remove(path)


@dp.callback_query_handler(text="about_me")
async def new_comment(call: CallbackQuery) -> None:
    await call.message.edit_text(text=("Kirim pesan tentang diri Anda"))
    await NewData.commentary.set()


@dp.message_handler(state=NewData.commentary)
async def update_comment_complete(message: types.Message, state: FSMContext) -> None:
    markup = await change_info_keyboard()
    try:
        censored = censored_message(message.text)
        await db_commands.update_user_data(
            commentary=quote_html(censored), telegram_id=message.from_user.id
        )
        await asyncio.sleep(0.2)
        await delete_message(message)
        await message.answer(
            text=("Komentar diterima!\n" "Pilih apa yang ingin Anda ubah: "),
            reply_markup=markup,
        )
        await state.reset_state()
    except DataError as ex:
        logger.error(f"Error in update_comment_complete {ex}")
        await message.answer(
            text=(
                "Telah terjadi kesalahan! Coba ubah deskripsinya lagi. "
                "Mungkin pesan Anda terlalu besar\n"
                "Jika kesalahan terus berlanjut, lapor ke @nazhak."
            )
        )
        return


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
                text=("Anda telah dikembalikan ke menu"), reply_markup=markup
            )
        else:
            await message.answer(
                text=(
                    "Anda memasukkan tautan atau nama akun yang salah.\n\nContoh:\n"
                    "<code>@fwabase</code>\n<code>https://www.instagram.com/fwabase</code>"
                )
            )

    except DataError:
        await message.answer(text=("Telah terjadi kesalahan. coba lagi"))
        return
