from aiogram import Router, types, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command, CommandObject
from aiogram.types import CallbackQuery, FSInputFile, WebAppInfo,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from src.db_controller import db
from aiogram.utils.deep_linking import create_start_link, decode_payload
from config_reader import config
from aiogram.filters import StateFilter
from middlewares.user_type_middleware import UserTypeMiddleware
router=Router()
user_frienfly_error_text="Произошла ошибка. Она уже отправлена разработчикам:("



                                                                                                                          

async def send_error_to_devs(msg: types.Message,error: str, error_text: Exception,bot: Bot,send_to_user=True):
    for i in config.admin_list.get_secret_value().split(','):
        await bot.send_message(i,f"<b>{error}</b>")
        await bot.send_message(i,f"Текст ошибки:\n\n{error_text}")
    if send_to_user:
        await msg.answer(user_frienfly_error_text)


async def make_movie_keyboard(movies)-> types.InlineKeyboardMarkup:
    buttons = []        
    
    counter=0
    for i in movies:
        if counter<7:
            buttons.append([types.InlineKeyboardButton(text=i[0], callback_data=str(i[1]))])
            counter+=1                                                                                        
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def get_film(callback: CallbackQuery,bot:Bot):
    try:


        if str(callback.from_user.id) in config.workers_list.get_secret_value().split(','):
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Удалить",
                callback_data=f"delete_{callback.data}"))


            if callback.data.startswith("https://t.me/"):            
                builder = InlineKeyboardBuilder()
                builder.add(types.InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"delete_{callback.data}"),
                    types.InlineKeyboardButton(
                        text="Перейти в канал",
                        url=callback.data
                    )
                )
                await callback.message.answer(f"Haжмите на кнопку",reply_markup=builder.as_markup(),protect_content=True)                                              
            else:
                await bot.copy_message(callback.from_user.id,from_chat_id=int(config.chat_id.get_secret_value()),message_id=callback.data,reply_markup=builder.as_markup(),protect_content=True)
        else:
            if callback.data.startswith("https://t.me/"):
                builder = InlineKeyboardBuilder()                                                                               
                builder.add(types.InlineKeyboardButton(
                        text="Перейти в канал",
                        url=callback.data
                    )
                )
                await callback.message.answer(f"Нажмите на кнопку",reply_markup=builder.as_markup(),protect_content=True)                                              
            else:
                await bot.copy_message(callback.from_user.id,from_chat_id=int(config.chat_id.get_secret_value()),message_id=callback.data,protect_content=True)
        await callback.message.delete()
    except Exception as e:
        print(e)
        await send_error_to_devs(callback.message,error=e,error_text="Ошибка при отправке фильма",bot=bot)

    #BASIC USER COMMANDS
#/Film Name
async def search_film(msg: types.Message, state: FSMContext, bot: Bot):
    try:
        movies=await db.get_movies(msg.text)
        if len(movies)==0:
            await msg.answer("Ничего не найдено, но запрос отправлен модераторам для добавления нового фильма:)") 
            await db.add_search_query(msg.text,msg.from_user.id)
        else:                                            
            b=await make_movie_keyboard(movies)

            await msg.answer("Результаты по запросу: "+msg.text,reply_markup=b)
    except Exception as e:
        await send_error_to_devs(msg,error=e,error_text="Ошибка при Поиске Фильма",bot=bot)




#/profile
async def profile(callback: CallbackQuery,bot: Bot):
    try:
        user_info=await db.get_user_info(callback.from_user.id)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Главная",
            callback_data="main")
        )

        if type(user_info) is Exception:
            await send_error_to_devs(callback.message,error=user_info,error_text="Ошибка при команде /profile",bot=bot)
        else:
            text=f"<b>Профиль:</b>\n\nРеферальная ссылка:\n{user_info[3]}\nКоличество рефералов:{user_info[4]}"
            pic=FSInputFile("res/profile.png")
            img=types.input_media_photo.InputMediaPhoto(media=pic,caption=text)
            await callback.message.edit_media(media=img,reply_markup=builder.as_markup())
    except Exception as e:
        print(e)
        await send_error_to_devs(callback.message,error=e,error_text="Ошибка при нажатии кнопки Профиль",bot=bot)

#/help
def command_builder(msg: types.Message) -> str:
    command_list="<b>Весь список комманд:</b>\n"
    start_cmd="/start - Перезапустить бота\n"
    help_cmd="/help - Все команды\n"
    gap="\n"
    text=command_list+start_cmd+help_cmd
    
    workers_list=config.workers_list.get_secret_value().split(',') 
    admin_list=config.admin_list.get_secret_value().split(',')
    

    if str(msg.from_user.id) in workers_list:
        add_film_cmd="/add - добавить новый фильм\n"
        popular_queries_cmd="/history - Топ 10 неудовлетворенных запросов\n"
        text+=gap+add_film_cmd+popular_queries_cmd
    
    if str(msg.from_user.id) in admin_list:
        make_ads_cmd="/new_post - Добавить рекламу\n"
        check_posts_cmd="/posts - Все отложенные посты\n"
        delete_post_cmd="/delete_post - Удалить отложенный пост\n"
        statistics_cmd="/statistics - Количество активных юзеров в день\nСреднее количество активных юзеров в неделю\nАктивные юзеры с рекламой\n"

        text+=gap+make_ads_cmd+check_posts_cmd+delete_post_cmd+statistics_cmd

    return text

async def help(msg: types.Message):
    await msg.answer(command_builder(msg))


#/start
async def increment_referral(msg: types.Message, command: CommandObject,bot: Bot):
    try:
        referral = command.args
        print(referral)
        if referral is not None:
            referral=int(decode_payload(referral))
            a=await db.increment_referrals(referral)
            b=await db.get_user_info(referral)
            if b[4]>=5:
                get_user=await db.get_user_info(referral)
                if get_user[5]:
                    await db.disable_ads(referral)
                    await bot.send_message(referral,"<b>Количество рефералов равно 1. Реклама отключена!</b>")

            await bot.send_message(referral,"<b>По вашей реферальной ссылке есть новый пользователь!</b>")
            if isinstance(a, Exception):
                await send_error_to_devs(msg,error=a,error_text="Ошибка при инкременте реферала",bot=bot,send_to_user=False)

    except Exception as e:
        print(e)
        return await send_error_to_devs(msg,error=e,error_text="Ошибка при инкременте реферала",bot=bot,send_to_user=False)


async def callback_start(callback: CallbackQuery,bot: Bot):
    try:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Профиль",
            callback_data="profile"),
            types.InlineKeyboardButton(
                text="Тех. Поддержка",
                url=config.help_chat.get_secret_value()
                )
        )
        pic=FSInputFile("res/main.png") 
        img=types.input_media_photo.InputMediaPhoto(media=pic)
        await callback.message.edit_media(media=img,reply_markup=builder.as_markup())
    except Exception as e:                                                                                                                           
        await send_error_to_devs(callback.message,error=e,error_text="Ошибка при нажатии кнопки Главная",bot=bot)

async def start(msg: types.Message, command: CommandObject,bot: Bot):
    try:
        user_info= await db.get_user_info(msg.from_user.id)
        
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Профиль",
            callback_data="profile"),
            types.InlineKeyboardButton(
                text="Тех. Поддержка",
                url=config.help_chat.get_secret_value()

                )
        )

        if user_info is None:
            await increment_referral(msg,command,bot)
            link = await create_start_link(bot,
                str(msg.from_user.id),
                encode=True)
            if msg.from_user.username is not None:
                a=await db.register_user(user_id=msg.from_user.id,
                            username=msg.from_user.username,
                            referral_link=link
                            )
            else:
                a=await db.register_user(user_id=msg.from_user.id,
                            username="NoneType",
                            referral_link=link
                            )

            if a is Exception:
                await send_error_to_devs(msg,"Ошибка при команде /start",a,bot)
            else:
                photo=FSInputFile("res/main.png")
                await bot.send_photo(msg.from_user.id,photo,reply_markup=builder.as_markup())
                await msg.answer("Чтобы найти фильм - просто введи название:)")
                await msg.answer("Если вы приведете 1 человека по реф. ссылке в профиле - \n<b>У Вас Навсегда Отключится Реклама!</b>")
                await db.increment_active_users(msg.from_user.id)
        else:
            photo=FSInputFile("res/main.png")
            await bot.send_photo(msg.from_user.id,photo,reply_markup=builder.as_markup())
            await msg.answer("Чтобы найти фильм - просто введи название:)")
            """
            await msg.answer(
                    "Test",
                    reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Open Webview", url='https://7e77-109-127-134-17.ngrok-free.app'
                        )
                    ]
                ]
            ),)"""

    except Exception as e:
        await send_error_to_devs(msg,error=e,error_text="Ошибка при команде /start",bot=bot)    
def register_handlers():                                                                                           
    
    work_l=config.workers_list.get_secret_value().split(',')
    adm_l=config.admin_list.get_secret_value().split(',')
    
    router.callback_query.register(profile, F.data=="profile")
    router.callback_query.register(callback_start,F.data=="main")
    router.callback_query.register(get_film, F.data.isdigit().__or__(F.data.startswith('https://t.me/')))
    router.message.middleware(UserTypeMiddleware(work_l,adm_l,"average"))
    router.message.register(search_film,F.text[0]!="/",StateFilter(None))
    router.message.register(start, Command('start'))
    router.message.register(help, Command('help'))
