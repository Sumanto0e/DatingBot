import uuid

from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)

from data.config import (
    load_config,
)
from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from keyboards.inline.payments_inline import (
    payment_menu_keyboard,
    yoomoney_keyboard,
)
from loader import (
    dp,
)
from utils.db_api import (
    db_commands,
)


@dp.callback_query_handler(text="unban")
async def get_payment_menu(call: CallbackQuery) -> None:
    await call.message.edit_text(
        text=(
            "<b>💳 hubungi @nazhak untuk unban</b>\n\n"
        ),
        reply_markup=await payment_menu_keyboard(),
    )
