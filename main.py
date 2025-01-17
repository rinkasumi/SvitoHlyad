import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config
from BaseModeration.muting import muting_router
from BaseModeration.ban import ban_router
from BaseModeration.kick import kick_router
from middlefilters.addUser import AddUserToDatabaseMiddleware
from database.models import init_db
from handlers.handlers import handlers_router
from BaseModeration.reports import report_router
from handlers.blockStickers import stick_router
from handlers.blockChannels import channels_router


async def main():
    await init_db()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(stick_router, muting_router, 
                       ban_router, report_router,
                       channels_router, kick_router,
                       handlers_router)
    dp.message.middleware(AddUserToDatabaseMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
