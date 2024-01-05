import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage
from handlers import main_logic, admin, worker
from middlewares.usage_middleware import UsageFrequencyMiddleware
from middlewares.subscription_middleware import SubscriptionMiddleware
from middlewares.throttling_middleware import ThrottlingMiddleware
from src.db_controller import db
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
#session = AiohttpSession(
#    api=TelegramAPIServer.from_base(config.api_host.get_secret_value()+':'+config.api_port.get_secret_value())
#)
# импорты

# Для записей с типом Secret* необходимо 
# вызывать метод get_secret_value(), 
# чтобы получить настоящее содержимое вместо '*******'
bot = Bot(token=config.bot_token.get_secret_value(),parse_mode="HTML")
storage=RedisStorage.from_url(config.redis_link.get_secret_value())
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
#@dp.message(Command("start"))
#async def cmd_start(message: types.Message):
#    await message.answer("Hello!")





# Запуск процесса поллинга новых апдейтов
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp.message.outer_middleware(ThrottlingMiddleware(storage))
    dp.callback_query.outer_middleware(ThrottlingMiddleware(storage))
    dp.update.outer_middleware(UsageFrequencyMiddleware())                                                                                                            
    dp.message.middleware(SubscriptionMiddleware())

    dp.include_router(main_logic.router)
    main_logic.register_handlers()
    
    dp.include_router(admin.router)
    admin.register_handlers()
    
    dp.include_router(worker.router)
    worker.register_handlers()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(db.init())
    asyncio.run(main())
    #logging.info("BOT STARTED")
