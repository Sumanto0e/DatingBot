import asyncio
from contextlib import (
    suppress,
)
import datetime
import os
import pathlib
import random
import re
import shutil
from typing import (
    Optional,
    Union,
)

import aiofiles
from aiogram import (
    types,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InputFile,
    Message,
    ReplyKeyboardRemove,
)
from aiogram.utils.exceptions import (
    BadRequest,
    MessageCantBeDeleted,
    MessageToDeleteNotFound,
)
from asyncpg import (
    UniqueViolationError,
)

from data.config import (
    load_config,
)
from keyboards.inline.menu_profile_inline import (
    get_profile_keyboard,
)
from functions.main_app.app_scheduler import (
    send_message_week,
)
from keyboards.inline.guide_inline import (
    create_pagination_keyboard,
)
from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from keyboards.inline.settings_menu import (
    information_keyboard,
)
from loader import (
    bot,
    logger,
    scheduler,
)
from utils.db_api import (
    db_commands,
)
from utils.db_api.db_commands import (
    check_user_meetings_exists,
)


async def delete_message(message: Message) -> None:
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


async def choice_gender(call: CallbackQuery) -> None:
    """Function that saves to the database the gender that the user has selected."""
    sex_mapping = {"male": "male", "female": "female"}

    selected_sex = sex_mapping.get(call.data)

    if selected_sex:
        try:
            await db_commands.update_user_data(
                telegram_id=call.from_user.id, need_partner_sex=selected_sex
            )
        except UniqueViolationError:
            pass


async def display_profile(call: CallbackQuery, markup: InlineKeyboardMarkup) -> None:
    """Function for displaying the user profile."""
    user = await db_commands.select_user(telegram_id=call.from_user.id)
    count_referrals = await db_commands.count_all_users_kwarg(
        referrer_id=call.from_user.id
    )
    user_verification = "✅" if user.verification else ""

    user_info_template = (
        "{name}, {age} tahun, {city}, {verification}\n\n{commentary}\n\n"
        "Filter pasangan anda:\n\n"
        "🚻 lawan jenis anda: {need_partner_sex}\n"
        "🔞 Rentang usia: {min}-{max} tahun\n\n"
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

    await call.message.answer_photo(
        caption=user_info, photo=user.photo_id, reply_markup=markup
    )


async def registration_menu(
    obj: Union[CallbackQuery, Message],
) -> None:
    support = await db_commands.select_user(
        telegram_id=load_config().tg_bot.support_ids[0]
    )
    markup = await start_keyboard(obj)
    heart = random.choice(["💙", "💚", "💛", "🧡", "💜", "🖤", "❤", "🤍", "💖", "💝"])
    text = (
        "Salam, {fullname}!!\n\n"
        "{heart} <b> Querendo </b> - Platform untuk mencari kenalan baru.\n\n"
        "🪧 Anda dapat bergabung dikomunitas kami - "
        "https://t.me/fwabasee \n\n"
        "https://t.me/menfesfwabasee \n\n"
        "@{supports}\n\n"
    ).format(fullname=obj.from_user.full_name, heart=heart, supports=support.username)
    try:
        await obj.message.edit_text(text=text, reply_markup=markup)
        scheduler.add_job(
            send_message_week,
            trigger="interval",
            weeks=1,
            jitter=120,
            args={obj.message},
        )
    except AttributeError:
        await obj.answer(text=text, reply_markup=markup)
        scheduler.add_job(
            send_message_week, trigger="interval", weeks=1, jitter=120, args={obj}
        )
    except BadRequest:
        await delete_message(obj.message)

        await obj.message.answer(text=text, reply_markup=markup)



async def check_user_in_db(telegram_id: int, message: Message, username: str) -> None:
    if not await db_commands.check_user_exists(
        telegram_id
    ) and not await check_user_meetings_exists(telegram_id):
        user = await db_commands.select_user_object(telegram_id=telegram_id)
        referrer_id = message.text[7:]
        if referrer_id != "" and referrer_id != telegram_id:
            await db_commands.add_user(
                name=message.from_user.full_name,
                telegram_id=telegram_id,
                username=username,
                referrer_id=referrer_id,
            )
            await db_commands.update_user_data(
                telegram_id=telegram_id, limit_of_views=user.limit_of_views + 15
            )
            await bot.send_message(
                chat_id=referrer_id,
                text=(
                    "Seorang pengguna mendaftar menggunakan tautan Anda{}!\n"
                    "Anda mendapat tambahan 15 ❤️"
                ).format(message.from_user.username),
            )
        else:
            await db_commands.add_user(
                name=message.from_user.full_name,
                telegram_id=telegram_id,
                username=username,
            )
        await db_commands.add_meetings_user(telegram_id=telegram_id, username=username)
        if telegram_id in load_config().tg_bot.admin_ids:
            await db_commands.add_user_to_settings(telegram_id=telegram_id)


async def finished_registration(
    state: FSMContext, telegram_id: int, message: Message
) -> None:
    await state.finish()
    await db_commands.update_user_data(telegram_id=telegram_id, status=True)

    user = await db_commands.select_user(telegram_id=telegram_id)

    markup = await start_keyboard(obj=message)

    text = (
        "Pendaftaran berhasil diselesaikan! \n\n "
        "{}, "
        "{} tahun, "
        "{}\n\n"
        "<b>status</b> - {}"
    ).format(user.varname, user.age, user.city, user.commentary)

    await message.answer_photo(caption=text, photo=user.photo_id, reply_markup=markup)


async def saving_normal_photo(
    message: Message, telegram_id: int, file_id: str, state: FSMContext
) -> None:
    """Fungsi yang menyimpan foto pengguna tanpa sensor."""
    try:
        await db_commands.update_user_data(telegram_id=telegram_id, photo_id=file_id)

        await message.answer(
            text=("Foto diambil!"), reply_markup=ReplyKeyboardRemove()
        )
    except Exception as err:
        logger.info(f"Kesalahan dalam saving_normal_photo | err: {err}")
        await message.answer(
            text=(
                "Telah terjadi kesalahan! Coba lagi atau kirim foto lain. \n"
                "Jika kesalahan terus berlanjut, lapor ke @nazhak."
            )
        )
    await finished_registration(state=state, telegram_id=telegram_id, message=message)


async def saving_censored_photo(
        message: Message,
        telegram_id: int,
        state: FSMContext,
        out_path: Union[str, pathlib.Path],
        flag: Optional[str] = "registration",
        markup: Union[InlineKeyboardMarkup, None] = None,
) -> None:
    """.Fungsi yang menyimpan foto pengguna dengan sensor."""
    photo = InputFile(out_path)
    id_photo = await bot.send_photo(
        chat_id=telegram_id,
        photo=photo,
        caption=(
            "Saat memeriksa foto Anda, kami menemukan konten yang mencurigakan!\n"
            "Itu sebabnya kami sedikit menyesuaikan foto Anda"
        ),
    )
    file_id = id_photo["photo"][0]["file_id"]
    await asyncio.sleep(1)
    try:
        await db_commands.update_user_data(telegram_id=telegram_id, photo_id=file_id)

    except Exception as err:
        logger.info(f"Kesalahan dalam saving_censored_photo | err: {err}")
        await message.answer(
            text=(
                "Telah terjadi kesalahan!"
                "Coba lagi atau kirim foto lain. \n"
                "Jika kesalahan terus berlanjut, lapor ke @nazhak."
            )
        )
    if flag == "change_datas":
        await message.answer(
            text=("<u>Foto diterima!</u>\n" "Pilih apa yang ingin Anda ubah: "),
            reply_markup=markup,
        )
        await state.reset_state()
    elif flag == "registration":
        await finished_registration(
            state=state, telegram_id=telegram_id, message=message
        )


async def update_normal_photo(
        message: Message,
        telegram_id: int,
        file_id: str,
        state: FSMContext,
        markup
) -> None:
    """Fungsi yang memperbarui foto pengguna."""
    try:
        await db_commands.update_user_data(telegram_id=telegram_id, photo_id=file_id)
        await message.answer(
            text=("Foto diambil!"), reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(3)
        await message.answer(
            text=("Pilih apa yang ingin Anda ubah: "), reply_markup=markup
        )
        await state.reset_state()
    except Exception as err:
        logger.info(f"Kesalahan dalam update_normal_photo | err: {err}")
        await message.answer(
            text=(
                "Telah terjadi kesalahan! Coba lagi atau kirim foto lain. \n"
                "Jika kesalahan terus berlanjut, lapor ke @nazhak."
            )
        )


async def dump_users_to_file():
    async with aiofiles.open("users.txt", "w", encoding="utf-8") as file:
        _text = ""
        _users = await db_commands.select_all_users()
        for user in _users:
            _text += str(user) + "\n"

        await file.write(_text)

    return "users.txt"


async def backup_configs():
    shutil.make_archive("backup_data", "zip", "./logs/")
    return "./backup_data.zip"


async def send_photo_with_caption(
        call: CallbackQuery,
        photo: str,
        caption: str,
        step: int,
        total_steps: int,
) -> None:
    markup = await create_pagination_keyboard(step, total_steps)

    await call.message.delete()
    await call.message.answer_photo(
        types.InputFile(photo), reply_markup=markup, caption=caption
    )


async def handle_guide_callback(
        call: CallbackQuery,
        callback_data: dict,
) -> None:
    step = int(callback_data.get("value"))

    photo_path = f"brandbook/{step}_page.png"
    caption = ("Panduan Bot: \n<b>Nomor Halaman.{}</b>").format(step)
    await send_photo_with_caption(
        call=call,
        photo=photo_path,
        caption=caption,
        step=step,
        total_steps=len(os.listdir("brandbook/")),
    )


async def information_menu(call: CallbackQuery) -> None:
    start_date = datetime.datetime(2024, 9, 16, 14, 0)
    now_date = datetime.datetime.now()
    delta = now_date - start_date
    count_users = await db_commands.count_users()
    markup = await information_keyboard()
    txt = (
        "Anda berada di bagian <b>Informasi</b> pada bot, di sini Anda dapat melihat: statistik,"
        "mengubah bahasa, dan juga melihat buku merek kami.\n\n"
        "🌐 Kami bekerja selama: <b>{}</b> hari\n"
        "👤 Jumlah pengguna: <b>{}</b>\n"
    ).format(delta.days, count_users)
    try:
        await call.message.edit_text(text=txt, reply_markup=markup)
    except BadRequest:
        await delete_message(call.message)
        await call.message.answer(text=txt, reply_markup=markup)


async def get_report_reason(call: CallbackQuery) -> str:
    match = re.search(r"report:(.*?):", call.data)
    reason_key = match.group(1)
    reason_mapping = {
        "adults_only": "🔞 Konten dewasa",
        "drugs": "💊 Pengedar narkoba",
        "scam": "💰 Penipuan",
        "another": "🦨 Lainnya",
    }
    return reason_mapping.get(reason_key, "Alasan yang tidak diketahui")
