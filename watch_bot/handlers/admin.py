from aiogram import Router, types, Bot
from aiogram.filters.command import Command, CommandObject
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from src.db_controller import db
from config_reader import config
from middlewares.user_type_middleware import UserTypeMiddleware
import datetime
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramForbiddenError



router=Router()
user_frienfly_error_text="Произошла ошибка. Она уже отправлена разработчикам:("





async def send_error_to_devs(msg: types.Message,error: str, error_text: Exception,bot: Bot):
    for i in config.admin_list.get_secret_value().split(','):
        await bot.send_message(i,f"<b>{error}</b>")
        await bot.send_message(i,f"Текст ошибки:\n\n{error_text}")
    await msg.answer(user_frienfly_error_text)

async def statistics(msg: types.Message,bot: Bot):
    active_users_per_day=str(await db.get_active_user_count(0))
    active_users_per_week=str(await db.get_active_user_count(7)/7)
    active_users_per_month=str(await db.get_active_user_count(30)/30)
    
    active_users_per_day_ads=str(await db.get_active_user_count_ads(0))
    active_users_per_week_ads=str(await db.get_active_user_count_ads(7)/7)
    active_users_per_month_ads=str(await db.get_active_user_count_ads(30)/30)
    
    all_users=str(await db.get_users_count())
    all_users_ads=str(await db.get_users_count_with_ads())
    text="<b>Все Активные Юзеры:</b>"+"\n"+active_users_per_day+"\n"+active_users_per_week+"\n"+active_users_per_month
    
    text+="\n\n<b>Активные Юзеры С Рекламой:</b>\n"+active_users_per_day_ads+"\n"+active_users_per_week_ads+"\n"+active_users_per_month_ads

    text+=f"\n\n<b>Все Юзеры:</b>\n{all_users}\nC рекламой: {all_users_ads}"

    

    await msg.answer(text)

                                                                                                                    

async def search_history(msg: types.Message):
    a=await db.get_search_history(10)
    text="<b>Топ 10 Запросов</b>\n"
    for i in a:
        text+=f"\n{i}"
    await msg.answer(text)


class AutoPostStates(StatesGroup):
    GetForwardedPost=State()
    GetButtons=State()
    GetTime=State()
    GetUserAmount=State()

    GetConfirmation=State()

    RemovePost=State()


async def remove_post_by_id(id: int):
    pass



async def new_post(msg: types.Message, state: FSMContext, bot: Bot):
    await msg.answer("Отправь рекламное сообщение")
    await state.set_state(AutoPostStates.GetForwardedPost)

async def send_post(msg: types.Message, state: FSMContext, bot: Bot):
    await state.set_state(AutoPostStates.GetButtons)
    await msg.answer("Теперь добавьте кнопки: (text+url)")
    await state.update_data(ads_post=msg)
    builder=InlineKeyboardBuilder()
    await state.update_data(builder=builder)
async def set_button(msg: types.Message, state: FSMContext, bot: Bot):
    a=await state.get_data()
    a=a['builder']
    a.row(types.InlineKeyboardButton(                                            
            text=msg.text.split("+")[0],
            url=msg.text.split("+")[1]
        ))
    await state.update_data(builder=a)
    await msg.answer("Добавлено! Если это всё - жмите /next")

async def confirm_buttons(msg: types.Message, state: FSMContext, bot: Bot):
    message=(await state.get_data())['ads_post']
    buttons=(await state.get_data())['builder']

    #await msg.answer("Теперь введите дату (год,месяц,день,час,минута)")
    await state.set_state(AutoPostStates.GetUserAmount)
    await state.update_data(ads_post=message)
    await state.update_data(builder=buttons)
    await state.update_data(time_set=datetime.datetime.now())
    await msg.answer("Теперь введи количество юзеров") 

def is_digit(s:str):
    return s.isdigit()
async def set_time(msg: types.Message, state: FSMContext, bot: Bot):
    time_to_set=msg.text.split()
    if not all(map(is_digit,time_to_set)):
        return await msg.answer("Некорректная дата!")
    time_to_set=list(map(int,time_to_set))
    if datetime.datetime(time_to_set[0],
                         time_to_set[1],
                         time_to_set[2],
                         time_to_set[3],
                         time_to_set[4]) <= datetime.datetime.now():
        return await msg.answer("Некорректная дата!")
    await state.set_state(AutoPostStates.GetUserAmount)
    
    time_to_set=datetime.datetime(time_to_set[0],
                         time_to_set[1],
                         time_to_set[2],
                         time_to_set[3],
                         time_to_set[4])
    await state.update_data(time_set=time_to_set)
    await msg.answer("Теперь введи количество юзеров") 
async def set_user_amount(msg: types.Message, state: FSMContext):
    if (await db.get_users_count()) >= int(msg.text):
        message=(await state.get_data())['ads_post']
        buttons=(await state.get_data())['builder']
        time_to_set=(await state.get_data())['time_set']
        await state.set_state(AutoPostStates.GetConfirmation)
        final_message=await message.send_copy(msg.from_user.id,reply_markup=buttons.as_markup())
        await msg.answer(f"Будет отправлено {time_to_set.year}.{time_to_set.month}.{time_to_set.day} \nв {time_to_set.hour}:{time_to_set.minute}")
        await state.update_data(message=final_message)
        await state.update_data(amount=int(msg.text))
        await msg.answer(f"Количество юзеров: {msg.text}")
        await msg.answer("Напишите да(нет), если все (не) корректно")
    else:
        await msg.answer("Слишком большое число юзеров:(")

async def confirm_post(msg:types.Message, state: FSMContext, bot: Bot):                                      
    try:
        if msg.text.lower()=="да":
            time= (await state.get_data())['time_set']
            post=(await state.get_data())['message']
            amount=(await state.get_data())['amount']
            post_channel_id=int(config.ads_chat_id.get_secret_value())
            b=await post.send_copy(post_channel_id)
            await db.add_post_id(b.message_id,time,amount)
        
            users=await db.get_users_tgids(amount)
        
            cn=0
            for i in users:
                try:
                    #await bot.get_user(i[1])
                    await post.send_copy(i[1])
                except TelegramForbiddenError as e:
                    print("banned")
                    continue
                else:
                    cn+=1
            await msg.answer(f"Всё по кайфy \nСообщение было отправлено {cn} юзерам")
        await state.clear()
    except Exception as e:
        print(e)
        await msg.answer("Ошибка!!")
async def post_list(msg: types.Message, state: FSMContext, bot: Bot):
    a=await db.get_all_posts()
    for i in a:
        await bot.copy_message(msg.from_user.id,from_chat_id=int(config.ads_chat_id.get_secret_value()),message_id=i[1])
        await msg.answer(f"Время: {i[2].year}.{i[2].month}.{i[2].day} {i[2].hour}:{i[2].minute}")
        await msg.answer(f"Количество юзеров: {i[3]}")

async def remove_post(msg: types.Message, state: FSMContext, bot: Bot):
    pass

async def stop(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отмена!")

def register_handlers():                                                                                           
    
    work_l=config.workers_list.get_secret_value().split(',')
    adm_l=config.admin_list.get_secret_value().split(',')
    
    router.message.middleware(UserTypeMiddleware(work_l,adm_l,"admin"))
    router.message.register(statistics, Command('statistics'))
    router.message.register(search_history, Command('history'))
    
    router.message.register(post_list,StateFilter(None),Command('posts'))
    router.message.register(new_post,StateFilter(None),Command('new_post'))
    router.message.register(send_post,StateFilter(AutoPostStates.GetForwardedPost),F.text[0]!="/")
    router.message.register(set_button,StateFilter(AutoPostStates.GetButtons),F.text.contains("+")) 
    router.message.register(confirm_buttons,StateFilter(AutoPostStates.GetButtons),Command('next'))
    router.message.register(set_time,StateFilter(AutoPostStates.GetTime),F.text.func(lambda text: len(text.split())==5))
    router.message.register(set_user_amount,StateFilter(AutoPostStates.GetUserAmount), F.text.isdigit())
    router.message.register(confirm_post,StateFilter(AutoPostStates.GetConfirmation),F.text.lower().in_({"да","нет"}))                                    
    router.message.register(stop,StateFilter(AutoPostStates),Command('stop'))

