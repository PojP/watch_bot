from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import TelegramObject
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
            if (await bot.get_chat_member(int(config.main_chat_id.get_secret_value()), user)).status is ChatMemberStatus.LEFT:
                await event.answer("Для использования подпишитесь на нас:)\nt.me/antihype_movie\nПосле подписки продолжайте использовать бота")
            else:
                return await handler(event,data)
