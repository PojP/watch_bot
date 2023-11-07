from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command, CommandObject
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from src.db_controller import db
from aiogram.utils.deep_linking import create_start_link, decode_payload
from config_reader import config

bot = None

user_frienfly_error_text="Произошла ошибка. Она уже отправлена разработчикам:("



                                                                                                                          


async def send_error_to_devs(msg: types.Message,error: str, error_text: Exception):
    for i in config.admin_list.get_secret_value().split(','):
        await bot.send_message(i,f"<b>{error}</b>")
        await bot.send_message(i,f"Текст ошибки:\n\n{error_text}")
    await msg.answer(user_frienfly_error_text)




#BASIC USER COMMANDS
#/Film Name
def search_film(msg: types.Message):
   pass 

#/profile
async def profile(msg: types.Message):
    user_info=await db.get_user_info(msg.from_user.id)
    
    print(type(user_info))
    if type(user_info) is Exception:
        await send_error_to_devs(msg,"Ошибка при команде /prifile",user_info)
    else:
        text=f"<b>Профиль:</b>\n\nРеферальная ссылка:\n{user_info[3]}\nКоличество рефералов:{user_info[4]}"

        await msg.answer(text)
#/help
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


#/start
async def get_refferal(msg: types.Message, command: CommandObject):
    args = command.args
    print(args)
    #await msg.answer(args)
    
    return args

async def increment_referral(referral,msg):
    if referral is not None:
        referral=decode_payload(referral)
        print(referral)
        a=await db.increment_referrals(referral)
        await bot.send_message(referral,"<b>По вашей реферальной ссылке есть новый пользователь!</b>")
        if isinstance(a, Exception):
            print(a)
            await send_error_to_devs(msg,"Ошибка при инкременте реферала",a)
async def start(msg: types.Message, command: CommandObject):
    user_info= await db.get_user_info(msg.from_user.id)
    print(user_info)
    if user_info is None:
        await increment_referral(await get_refferal(msg,command),msg)
        
        link = await create_start_link(bot,
                str(msg.from_user.id),
                encode=True)
        print(link)
        a=await db.register_user(user_id=msg.from_user.id,
                            username=msg.from_user.username,
                            referral_link=link
                            )
        print(a)
        if a is Exception:
            await send_error_to_devs(msg,"Ошибка при команде /start",a)
        else:
            await msg.answer("Привет! Это бот для просмотра фильмов. Просто введи название и получи фильм:)\nВесь список команд - /help")
    else:
        await msg.answer("Привет! Это бот для просмотра фильмов. Просто введи название и получи фильм:)\nВесь список команд - /help")

def register_handlers(dp: Dispatcher, bot_: Bot):
    global bot
    bot =bot_
    dp.message.register(start, Command('start'))
    dp.message.register(help, Command('help'))
    dp.message.register(profile,Command('profile'))
