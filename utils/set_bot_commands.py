import logging

from aiogram import (
    Dispatcher,
    types,
)

from data.config import (
    load_config,
)


async def set_user_commands(
        dp: Dispatcher, user_id: int, commands: list[types.BotCommand]
):
    try:
        await dp.bot.set_my_commands(
            commands=commands, scope=types.BotCommandScopeChat(user_id)
        )
    except Exception as ex:
        logging.error(f"{user_id}: Commands are not installed. {ex}")


async def set_default_commands(dp: Dispatcher) -> None:
    default_commands = [
        types.BotCommand("start", "🟢 Luncurkan bot"),
    ]

    admin_commands = [
        types.BotCommand("admin", "⚒ Menu Admin"),
        types.BotCommand("users", "🫂 Pengguna"),
        types.BotCommand("settings", "⚙️ Pengaturan"),
        types.BotCommand("ad", "📊 Periklanan"),
        types.BotCommand("logs", "🗒 Log"),
    ]

    await dp.bot.set_my_commands(default_commands, scope=types.BotCommandScopeDefault())

    for admin_id in load_config().tg_bot.admin_ids:
        await set_user_commands(dp, admin_id, admin_commands + default_commands)
