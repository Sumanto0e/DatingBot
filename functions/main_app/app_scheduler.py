from aiogram.types import (
    Message,
)

from keyboards.inline.questionnaires_inline import (
    viewing_ques_keyboard,
)
from loader import (
    bot,
)
from utils.db_api import (
    db_commands,
)


async def send_message_week(message: Message) -> None:
    user = await db_commands.select_user(telegram_id=message.from_user.id)
    text = (
        "Beberapa {} dari kota {} ingin bertemu denganmu sekarang"
    ).format(user_gender, user.need_city)

    await bot.send_message(
        chat_id=message.chat.id, text=text, reply_markup=await viewing_ques_keyboard()
    )
