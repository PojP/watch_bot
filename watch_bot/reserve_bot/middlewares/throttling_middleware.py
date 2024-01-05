import datetime
from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from datetime import timedelta

from aiogram.fsm.storage.redis import RedisStorage

class ThrottlingMiddleware(BaseMiddleware):
    time_updates: dict[int, datetime.datetime] = {}
    timedelta_limiter: datetime.timedelta = datetime.timedelta(seconds=0.3)
    
    def __init__(self,storage: RedisStorage):
        self.storage=storage

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not await self.storage.redis.get(name=event.from_user.id):
            await self.storage.redis.set(name=event.from_user.id,value=1,ex=1)
            return await handler(event, data)
        return
