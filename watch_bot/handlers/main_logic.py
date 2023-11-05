from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

bot = None













async def start(msg: types.Message):
    await msg.answer("Привет! Это бот для загрузки видео из TikTok и YouTube. Просто введите ссылку и получите видео. Удачи:)")

def register_handlers(dp: Dispatcher, bot_: Bot):
    global bot
    bot =bot_
    dp.message.register(start, Command('start'))
