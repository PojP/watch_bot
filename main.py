import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession

from handlers import main_logic


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
session = AiohttpSession(
    api=TelegramAPIServer.from_base(config.api_host.get_secret_value()+':'+config.api_port.get_secret_value())
)
# импорты

# Для записей с типом Secret* необходимо 
# вызывать метод get_secret_value(), 
# чтобы получить настоящее содержимое вместо '*******'
bot = Bot(token=config.bot_token.get_secret_value(),parse_mode="HTML",session=session)

# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
#@dp.message(Command("start"))
#async def cmd_start(message: types.Message):
#    await message.answer("Hello!")





# Запуск процесса поллинга новых апдейтов
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    main_logic.register_handlers(dp,bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    #logging.info("BOT STARTED")
