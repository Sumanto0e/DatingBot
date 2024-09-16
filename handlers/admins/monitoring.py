from aiogram import (
    types,
)
from aiogram.dispatcher import FSMContext

from filters.IsAdminFilter import (
    IsAdmin,
)
from functions.dating.create_forms_funcs import (
    monitoring_questionnaire,
)
from keyboards.inline.admin_inline import (
    start_monitoring_keyboard,
)
from keyboards.inline.questionnaires_inline import (
    action_keyboard_monitoring,
)
from loader import (
    dp,
)
from utils.db_api import (
    db_commands,
)


@dp.message_handler(IsAdmin(), text="👀 Pemantauan")
async def admin_monitoring(message: types.Message) -> None:
    await message.answer(
        text=("Untuk mulai memantau, klik tombol di bawah"),
        reply_markup=await start_monitoring_keyboard(),
    )


@dp.callback_query_handler(text="confirm_send_monitoring")
async def confirm_send_monitoring(call: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await monitoring_questionnaire(call, state)
    except IndexError:
        pass


# FIXME: мониторинг: IndexError
@dp.callback_query_handler(action_keyboard_monitoring.filter(action="ban"))
async def ban_form_owner(call: types.CallbackQuery, state: FSMContext) -> None:
    target_id = call.data.split(":")[2]
    await db_commands.update_user_data(telegram_id=target_id, is_banned=True)
    await call.answer("Profil pengguna telah diblokir")
    await monitoring_questionnaire(call, state)


@dp.callback_query_handler(action_keyboard_monitoring.filter(action="next"))
async def next_form_owner(call: types.CallbackQuery, state: FSMContext) -> None:
    await monitoring_questionnaire(call, state)
