import logging
from typing import (
    Any,
)

from aiogram import (
    Bot,
    Dispatcher,
    types,
)
from aiogram.contrib.fsm_storage.memory import (
    MemoryStorage,
)
from aiogram.contrib.fsm_storage.redis import (
    RedisStorage2,
)
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)
from nudenet import (
    NudeDetector,
)

from data.config import (
    load_config,
)


bot = Bot(token=load_config().tg_bot.token, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2() if load_config().tg_bot.use_redis else MemoryStorage()
dp = Dispatcher(bot, storage=storage)
job_defaults = dict(coalesce=False, max_instances=3)
scheduler = AsyncIOScheduler(
    timezone=load_config().tg_bot.timezone, job_defaults=job_defaults
)
detector = NudeDetector()

logger = logging.getLogger(__name__)
