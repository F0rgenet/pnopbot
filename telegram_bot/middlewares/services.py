from typing import Callable, Dict, Any, Awaitable, cast

from aiogram import BaseMiddleware
from aiogram.types import Update, TelegramObject
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot.services import *


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Update, data: Dict[str, Any]) -> Any:

        session = cast(AsyncSession, data.get("session"))
        user_service = UserService(session)
        if event.callback_query:
            telegram_user = event.callback_query.from_user
        elif event.message:
            telegram_user = event.message.from_user
        else:
            logger.warning("Пользователь для middleware не найден")
            return handler(event, data)
        user = await user_service.get_or_create_user(
            telegram_id=telegram_user.id,
            username=telegram_user.username
        )
        data['user'] = user
        return await handler(event, data)


class ServiceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        session = cast(AsyncSession, data.get('session'))
        data['task_service'] = TaskService(session)
        data['category_service'] = CategoryService(session)
        data['user_service'] = UserService(session)
        data['group_service'] = GroupService(session)
        return await handler(event, data)
