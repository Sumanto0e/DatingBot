from aiogram import (
    types,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.utils.exceptions import (
    BadRequest,
)

from handlers.users.back import (
    delete_message,
)
from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from keyboards.inline.support_inline import (
    cancel_support,
    cancel_support_callback,
    check_support_available,
    get_support_manager,
    support_callback,
    support_keyboard,
)
from loader import (
    bot,
    dp,
)


@dp.callback_query_handler(text="support")
async def ask_support_call(call: types.CallbackQuery) -> None:
    text = ("Ingin menghubungi dukungan teknis? Klik tombol di bawah!")
    keyboard = await support_keyboard(messages="many")
    try:
        if not keyboard:
            await call.message.edit_text(
                text=(
                    "Sayangnya, saat ini tidak ada operator yang tersedia. Coba lagi nanti."
                )
            )
            return
        await call.message.edit_text(text, reply_markup=keyboard)
    except BadRequest:
        await delete_message(message=call.message)
        await call.message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(support_callback.filter(messages="many", as_user="yes"))
async def send_to_support_call(
        call: types.CallbackQuery, state: FSMContext, callback_data: dict
) -> None:
    await call.message.edit_text(
        text=("Anda telah menghubungi dukungan teknis. Kami menunggu tanggapan dari operator!")
    )

    user_id = int(callback_data.get("user_id"))
    if not await check_support_available(user_id):
        support_id = await get_support_manager()
    else:
        support_id = user_id

    if not support_id:
        await call.message.edit_text(
            text=("Seorang pengguna ingin menghubungi Anda.")
        )
        await state.reset_state()
        return

    await state.set_state("wait_in_support")
    await state.update_data(second_id=support_id)

    keyboard = await support_keyboard(messages="many", user_id=call.from_user.id)

    await bot.send_message(
        chat_id=support_id,
        text=("Seorang pengguna ingin menghubungi Anda {full_name}").format(
            full_name=call.from_user.full_name
        ),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(support_callback.filter(messages="many", as_user="no"))
async def answer_support_call(
        call: types.CallbackQuery, state: FSMContext, callback_data: dict
) -> None:
    second_id = int(callback_data.get("user_id"))
    user_state = dp.current_state(user=second_id, chat=second_id)

    if str(await user_state.get_state()) != "wait_in_support":
        await call.message.edit_text("Sayangnya, pengguna sudah berubah pikiran.")
        return

    await state.set_state("in_support")
    await user_state.set_state("in_support")

    await state.update_data(second_id=second_id)

    keyboard = cancel_support(second_id)
    keyboard_second_user = cancel_support(call.from_user.id)

    await call.message.edit_text(
        text=(
            "Anda berhubungan dengan pengguna!\n"
            "Untuk mengakhiri percakapan, klik tombol."
        ),
        reply_markup=keyboard,
    )

    await bot.send_message(
        chat_id=second_id,
        text=(
            "Dukungan teknis menghubungi! Anda dapat menulis pesan Anda di sini. \n"
            "Untuk mengakhiri percakapan, klik tombol."
        ),
        reply_markup=keyboard_second_user,
    )


@dp.message_handler(state="wait_in_support", content_types=types.ContentTypes.ANY)
async def not_supported(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    second_id = data.get("second_id")

    keyboard = cancel_support(second_id)
    await message.answer(
        text=("Tunggu hingga operator merespons atau membatalkan sesi"), reply_markup=keyboard
    )


@dp.callback_query_handler(
    cancel_support_callback.filter(), state=["in_support", "wait_in_support", None]
)
async def exit_support(
        call: types.CallbackQuery, state: FSMContext, callback_data: dict
) -> None:
    markup = await start_keyboard(obj=call)
    user_id = int(callback_data.get("user_id"))
    second_state = dp.current_state(user=user_id, chat=user_id)
    if await second_state.get_state() is not None:
        await second_state.reset_state()
        await bot.send_message(
            chat_id=user_id, text=("Pengguna telah menyelesaikan sesi dukungan teknis")
        )

    await call.message.edit_text(
        text=("Anda telah mengakhiri sesi Anda dan telah kembali ke menu utama"),
        reply_markup=markup,
    )
    await state.reset_state()
