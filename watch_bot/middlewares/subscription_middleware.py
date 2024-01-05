from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import TelegramObject, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.chat_member_left import ChatMemberLeft
from src.db_controller import db
from config_reader import config

class SubscriptionMiddleware(BaseMiddleware):
    # Разумеется, никакого сервиса у нас в примере нет,
    # а только суровый рандом:

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user=data['event_from_user'].id
        bot=data['bot']
        a=await db.get_user_info(user)
        if a is None:
            if "/start" in event.text: 
                return await handler(event,data)
        else:
            reserve_bot = config.reserve_bot.get_secret_value()
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Наш канал",url="https://t.me/antihype_movie"),
                    InlineKeyboardButton(
                    text="Наш резервный бот",
                    url=reserve_bot
                    ))

            if (await bot.get_chat_member(int(config.main_chat_id.get_secret_value()), user)).status is ChatMemberStatus.LEFT or not await db.check_reserve_following(user,reserve_bot):
                await bot.send_message(user,text="Для использования подпишитесь на нас:)\nПосле подписки заново введите то, что пытались",reply_markup=builder.as_markup())
            else:                                                                                                                                                                                                  
                return await handler(event,data)

