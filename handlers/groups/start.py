from aiogram.dispatcher.filters import (
    Command,
)
from aiogram.types import (
    Message,
)

from filters.FiltersChat import (
    IsGroup,
)
from filters.IsAdminFilter import (
    IsAdmin,
)
from loader import (
    dp,
)


@dp.message_handler(IsGroup(), IsAdmin(), Command("start"))
async def start_group_handler(message: Message) -> None:
    await message.answer(
        text=(
            "<b>Hai, saya bot dari proyek FWA Group, untuk memverifikasi profil kencan</b>\n\n"
        )
    )
