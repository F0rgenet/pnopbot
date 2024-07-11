from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram_dialog import DialogManager
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot.database.orm import Database


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:
        async with Database() as session:
            data['session'] = session
            return await handler(event, data)
