from aiogram import Router, types, Bot
from aiogram.filters.command import Command, CommandObject
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from src.db_controller import db
from aiogram.utils.deep_linking import create_start_link, decode_payload
from config_reader import config
from middlewares.user_type_middleware import UserTypeMiddleware
router=Router()
user_frienfly_error_text="Произошла ошибка. Она уже отправлена разработчикам:("



class AddingMovieState(StatesGroup):
    movie_video=State()
    movie_title=State()

async def send_error_to_devs(msg: types.Message,error: str, error_text: Exception,bot: Bot):
    for i in config.admin_list.get_secret_value().split(','):
        await bot.send_message(i,f"<b>{error}</b>")
        await bot.send_message(i,f"Текст ошибки:\n\n{error_text}")
    await msg.answer(user_frienfly_error_text)







async def add_new_film(msg: types.Message, state: FSMContext, bot: Bot):
    await msg.answer("Скинь видео")
    await state.set_state(AddingMovieState.movie_video)


async def get_video(msg: types.Message,state: FSMContext, bot: Bot):
    await msg.answer("Теперь скинь название фильма")
    

    await state.set_state(AddingMovieState.movie_title)

async def get_text(msg: types.Message,state: FSMContext, bot: Bot):
    







def register_handlers():
    
    work_l=config.workers_list.get_secret_value().split(',')
    adm_l=config.admin_list.get_secret_value().split(',')
    
    router.message.middleware(UserTypeMiddleware(work_l,adm_l,"worker"))

    router.message.register(add_new_film, Command('start'))
    router.message.register(get_video, Command('help'),)
