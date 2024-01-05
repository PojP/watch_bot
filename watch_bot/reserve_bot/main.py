import asyncio
import logging
from aiogram import Bot, Dispatcher
from config_reader import config
from aiogram.fsm.storage.redis import RedisStorage
from handlers import main_logic
from middlewares.throttling_middleware import ThrottlingMiddleware
from src.db_controller import db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value(),parse_mode="HTML")
storage=RedisStorage.from_url(config.redis_link.get_secret_value())

dp = Dispatcher()



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp.message.outer_middleware(ThrottlingMiddleware(storage))
    dp.include_router(main_logic.router)
    main_logic.register_handlers()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(db.init())
    asyncio.run(main())
