import asyncio
from typing import (
    NoReturn,
    Union,
)

from aiogram import (
    types,
)
from aiogram.dispatcher.handler import (
    CancelHandler,
)
from aiogram.dispatcher.middlewares import (
    BaseMiddleware,
)

from data.config import (
    load_config,
)
from keyboards.inline.necessary_links_inline import (
    necessary_links_keyboard,
)
from loader import (
    bot,
)
from utils.db_api import (
    db_commands,
)

class fwalink:
    link = ("t.me/fwabasee")
    telegram_link_id = -1001771712186
    title = ("join comunnity")

class LinkCheckMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict) -> None:
        if isinstance(message.chat.type, types.ChatType):
            await self._check_links_and_handle(message.from_user.id, obj=message)

    async def on_process_callback_query(
            self, call: types.CallbackQuery, data: dict
    ) -> None:
        await self._check_links_and_handle(call.from_user.id, obj=call)

    @staticmethod
    async def _check_links_and_handle(
            user_id: int, obj: Union[types.CallbackQuery, types.Message]
    ) -> NoReturn:
        channels = ["@fwabasee"]
        for i in channels:
            check = await bot.get_chat_member(i, user_id)
            if check.status != 'left':
                pass
            else:
                await obj.message.answer("Anda belum berlangganan semua saluran! Untuk terus menggunakan bot, berlangganan! Tautan di bawah: @fwabase")
        return True
        
