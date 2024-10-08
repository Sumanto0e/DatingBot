from aiogram import (
    types,
)
from aiogram.types import (
    InlineKeyboardButton,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)
from aiogram.utils.markdown import (
    hcode,
)

from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from keyboards.inline.questionnaires_inline import (
    stopped_keyboard,
)
from loader import (
    dp,
    logger,
    bot,
)
from functions.dating import (
    ChooseReportReason,
    DislikeAction,
    DislikeReciprocity,
    GoBackToViewing,
    LikeAction,
    LikeReciprocity,
    SendReport,
    StartFindingFailure,
    StartFindingReachLimit,
    StartFindingSuccess,
    StoppedAction,
)


@dp.message_handler(state=None)
async def bot_echo(message: types.Message) -> None:
    await message.answer("opsi tidak ditemuka, silahkan ketik /start")


@dp.message_handler(state="*")
async def bot_echo_all(message: types.Message, state: FSMContext) -> None:
    state_name = await state.get_state()
    text = [
        f"Opsi tidak ditemukan {hcode(state_name)}",
        "Isi pesan:",
        hcode(message.text),
    ]
    await message.answer("opsi tidak ditemukan", reply_markup=await stopped_keyboard(message.from_user.id
))


@dp.callback_query_handler()
async def cq_echo(call: CallbackQuery) -> None:
    logger.debug(call.data)


@dp.message_handler(state="finding")
async def echo_message_finding(message: types.Message, state: FSMContext) -> None:
    await message.answer(("Menu: "), reply_markup=await start_keyboard(message))
    await state.reset_state()
