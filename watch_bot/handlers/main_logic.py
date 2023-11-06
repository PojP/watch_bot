from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

from config_reader import config

bot = None

 




def command_builder(msg: types.Message) -> str:
    command_list="<b>Весь список комманд:</b>\n"
    start_cmd="/start - Перезапустить бота\n"
    help_cmd="/help - Все команды\n"
    profile_cmd="/profile - Количество рефералов и собственная реферальная ссылка\n"
    gap="\n"
    text=command_list+start_cmd+help_cmd+profile_cmd
    
    workers_list=config.workers_list.get_secret_value().split(',') 
    admin_list=config.admin_list.get_secret_value().split(',')
    

    if str(msg.from_user.id) in workers_list:
        add_film_cmd="/add_film - добавить новый фильм\n"
        popular_queries_cmd="/queries - Топ 10 неудовлетворенных запросов\n"
        text+=gap+add_film_cmd+popular_queries_cmd
    
    if str(msg.from_user.id) in admin_list:
        make_ads_cmd="/make_ads - Добавить рекламу\n"
        check_posts_cmd="/check_posts - Все отложенные посты\n"
        delete_post_cmd="/delete_post - Удалить отложенный пост\n"
        statistics_cmd="/statistics - Количество активных юзеров в день\nСреднее количество активных юзеров в неделю\nАктивные юзеры с рекламой\n"

        text+=gap+make_ads_cmd+check_posts_cmd+delete_post_cmd+statistics_cmd

    return text


async def help(msg: types.Message):
    await msg.answer(command_builder(msg))

async def start(msg: types.Message):
    await msg.answer("Привет! Это бот для просмотра фильмов. Просто введи название и получи фильм:)\nВесь список команд - /help")

def register_handlers(dp: Dispatcher, bot_: Bot):
    global bot
    bot =bot_
    dp.message.register(start, Command('start'))
    dp.message.register(help, Command('help'))
