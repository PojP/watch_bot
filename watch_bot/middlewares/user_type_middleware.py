from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class UserTypeMiddleware(BaseMiddleware):
    # Разумеется, никакого сервиса у нас в примере нет,
    # а только суровый рандом:
    def __init__(self, worker_list, admin_list,user_level):
        self.admin_list=admin_list
        self.worker_list=worker_list
        self.user_level=user_level
        self.levels={
                "admin":3,
                "worker":2,
                "average":1
                }
    def get_user_type(self,user_id: int):
        if str(user_id) in self.admin_list:
            return 3
        elif str(user_id) in self.worker_list:
            return 2
        else:
            return 1

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        user_type = self.get_user_type(user.id)
        level=self.levels[self.user_level]
        if user_type>=level:
            return await handler(event,data)
        return 

