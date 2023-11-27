from aiogram import Router, types, Bot
from aiogram.filters import StateFilter,Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from src.db_controller import db
from config_reader import config
from middlewares.user_type_middleware import UserTypeMiddleware
router=Router()
user_frienfly_error_text="Произошла ошибка. Она уже отправлена разработчикам:("



class AddingMovieState(StatesGroup):
    movie_video=State()
    movie_title=State()
    movie_year=State()
    movie_confirm=State()


    

async def send_error_to_devs(msg: types.Message,error: str, error_text: Exception,bot: Bot):
    for i in config.admin_list.get_secret_value().split(','):
        await bot.send_message(i,f"<b>{error}</b>")
        await bot.send_message(i,f"Текст ошибки:\n\n{error_text}")
    await msg.answer(user_frienfly_error_text)







async def add_new_film(msg: types.Message, state: FSMContext, bot: Bot):
    await msg.answer("Скинь видео")
    await state.set_state(AddingMovieState.movie_video)

async def add_title(msg: types.Message,state: FSMContext, bot:Bot):
    await msg.answer("Теперь скинь название фильма")
    await state.set_state(AddingMovieState.movie_title)
    await state.update_data(video_msg=msg)


async def add_year(msg: types.Message, state: FSMContext,bot: Bot):
    await msg.answer("Теперь введи год. Если года нет - /next")
    await state.set_state(AddingMovieState.movie_year)
    await state.update_data(title=msg.text)

async def confirm(msg: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(year=msg.text)

    data = await state.get_data()
    title=data['title']
    year=data['year']

    await data['video_msg'].copy_to(msg.from_user.id,caption=f"{title}\n{year}")
    await msg.answer(f"Название: {title}\nГод: {year}")                                                                
    await msg.answer("Вы ввели такие данные. Подтвердить?")                                                    
    await state.set_state(AddingMovieState.movie_confirm)

async def confirm_next(msg: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(year=None)

    data = await state.get_data()
    title=data['title']
    year=data['year']

    await data['video_msg'].copy_to(msg.from_user.id,caption=f"{title}\n{year}")
    await msg.answer(f"Название: {title}\nГод: {title}")                                                                
    await msg.answer("Вы ввели такие данные. Подтвердить?")                                                    
    await state.set_state(AddingMovieState.movie_confirm)

async def get_confirmation(msg: types.Message, state: FSMContext, bot: Bot):
    try:
        if msg.text.lower()=="да":
            data=await state.get_data()
            print(data['title'])
            db_movies=await db.get_movies_for_add(data['title'],data['year'])
            print(db_movies)
            sended_movie=await data['video_msg'].copy_to(int(config.chat_id.get_secret_value()),caption=f"{data['title']}\n{data['year']}")
            await db.add_movie(data['title'],sended_movie.message_id,int(data['year']))
            if db_movies is not None:
                await db.delete_movie_by_tg_id(db_movies)
                await bot.delete_message(int(config.chat_id.get_secret_value()),int(db_movies))
                await msg.answer("Старый фильм удален!")
            await msg.answer("Все по кайфу")
            await state.clear()

        else:
            await state.clear()
            await msg.answer("Отмена")
    except Exception as e:
        await state.clear()
        print(e)

async def stop(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отмена")






def register_handlers():
    
    work_l=config.workers_list.get_secret_value().split(',')
    adm_l=config.admin_list.get_secret_value().split(',')
    
    router.message.middleware(UserTypeMiddleware(work_l,adm_l,"worker"))

    router.message.register(add_new_film, Command('add'),StateFilter(None))
    router.message.register(add_title,StateFilter(AddingMovieState.movie_video),F.video.is_not(None))
    router.message.register(add_year,StateFilter(AddingMovieState.movie_title))
    router.message.register(confirm,StateFilter(AddingMovieState.movie_year), F.text.isdigit())
    router.message.register(confirm_next,StateFilter(AddingMovieState.movie_year), Command('/next'))
    router.message.register(get_confirmation,StateFilter(AddingMovieState.movie_confirm),F.text.lower().in_({"да","нет"}))
    router.message.register(stop,StateFilter(AddingMovieState),Command('stop'))
