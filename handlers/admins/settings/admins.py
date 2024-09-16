from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
    Message,
)

from data.config import (
    change_env,
    load_config,
)
from filters.IsAdminFilter import (
    IsAdmin,
)
from keyboards.admin.inline.reply_menu import (
    admin_cancel_keyboard,
    settings_keyboard,
)
from keyboards.admin.inline.setting import (
    add_admins_keyboard,
)
from loader import (
    dp,
)
from states.admins import (
    AdminsActions,
)
from utils.set_bot_commands import (
    set_default_commands,
)


@dp.callback_query_handler(IsAdmin(), text="admin:admins")
async def admins_handler(call: CallbackQuery):
    text = (
        "<u>👮‍♂️ Аadministrator: </u>\n"
        f"<code>{load_config().tg_bot.admin_ids}</code>"
    )
    await call.message.edit_text(text, reply_markup=await add_admins_keyboard())


@dp.callback_query_handler(IsAdmin(), text=["admin:admins:add", "admin:admins:delete"])
async def admins_actions_handler(call: CallbackQuery):
    actions = {
        "admin:admins:add": [
            "<b>👮‍♂️ Masukkan ID Administrator untuk ditambahkan: </b>",
            AdminsActions.add,
        ],
        "admin:admins:delete": [
            "<b>👮‍♂️ Masukkan ID Administrator yang akan dihapus: </b>",
            AdminsActions.delete,
        ],
    }

    await call.message.edit_text(
        actions[call.data][0], reply_markup=await admin_cancel_keyboard()
    )
    await actions[call.data][1].set()


@dp.message_handler(IsAdmin(), state=AdminsActions.add)
async def admin_add_handler(message: Message, state: FSMContext):
    admins = load_config().tg_bot.admin_ids
    if message.text.isdigit():
        await state.finish()

        new_admin_id = int(message.text)

        if new_admin_id not in admins:
            admins += [
                new_admin_id,
            ]
            change_env("ADMINS", ", ".join([str(x) for x in admins]))

            await set_default_commands(dp)
            await message.answer(
                "<b>👮‍♂️ Administrator menambahkan!</b>",
                reply_markup=await add_admins_keyboard(),
            )
        else:
            await message.answer(
                "<b>🚫 ID ini sudah ada di tim admin!</b>",
                reply_markup=await admin_cancel_keyboard(),
            )
    else:
        await message.answer(
            "<b>🚫 Masukkan ID administrator baru: </b>",
            reply_markup=await admin_cancel_keyboard(),
        )


@dp.message_handler(IsAdmin(), state=AdminsActions.delete)
async def admin_delete_handler(message: Message, state: FSMContext):
    await state.finish()
    admins = load_config().tg_bot.admin_ids
    admin_id = int(message.text)

    if admin_id in admins:
        admins.remove(admin_id)
        change_env("ADMINS", ", ".join([str(x) for x in admins]))

        await set_default_commands(dp)
        await message.answer(
            text="<b>👮‍♂️ Administrator dihapus!</b>",
            reply_markup=await add_admins_keyboard(),
        )
    else:
        await message.answer(
            text="<b>🚫 ID ini bukan bagian dari tim admin!</b>",
            reply_markup=await admin_cancel_keyboard(),
        )


@dp.callback_query_handler(IsAdmin(), text="admin:settings")
async def back_to_admin_comp(call: CallbackQuery):
    await call.message.edit_text(
        text="<u>⚙️ Pengaturan</u>", reply_markup=await settings_keyboard()
    )
