from aiogram import Router, types, Bot
from aiogram.filters.command import Command
from src.db_controller import db
from config_reader import config


router=Router()
user_frienfly_error_text="Произошла ошибка. Она уже отправлена разработчикам:("



                                                                                                                          

async def send_error_to_devs(msg: types.Message,error: str, error_text: Exception,bot: Bot,send_to_user=True):

    for i in config.admin_list.get_secret_value().split(','):
        await bot.send_message(i,f"<b>{error}</b>")
        await bot.send_message(i,f"Текст ошибки:\n\n{error_text}")
    if send_to_user:
        await msg.answer(user_frienfly_error_text)


async def start(msg: types.Message,bot: Bot):
    try:
        res_bot=config.reserve_bot.get_secret_value()
        print('res bot getted')
        a=await db.add_user_to_reserve_list(msg.from_user.id,res_bot)
        print('added')
        if a:

            print('here')
            print(a)
            await send_error_to_devs(msg,error=a,error_text="Ошибка при команде /start в бд",bot=bot)
        else:
            await msg.answer("Вы успешно сохранили нашего бота в случае блокировки!")
    


    except Exception as e:
        print(e)
        await send_error_to_devs(msg,error=e,error_text="Ошибка при команде /start",bot=bot)    
def register_handlers():                                                                                           
    router.message.register(start, Command('start'))

