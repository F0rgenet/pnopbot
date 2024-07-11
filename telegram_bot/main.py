import os

from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.token import TokenValidationError
from aiogram.filters import ExceptionTypeFilter
from aiogram.exceptions import TelegramUnauthorizedError

from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnregisteredDialogError

from telegram_bot.database import register_models, dispose_database
from telegram_bot.handlers.error import on_unknown_intent, on_unregistered_dialog
from telegram_bot.middlewares import *
from .handlers import router as handlers_router


async def on_startup(dispatcher: Dispatcher):
    await register_models()
    dispatcher.include_router(handlers_router)
    logger.success("Бот запущен")


async def on_shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    logger.success("Бот остановлен")
    await dispose_database()


async def startup():
    logger.info("Запуск бота...")
    fsm_storage = MemoryStorage()
    dispatcher = Dispatcher(storage=fsm_storage)
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)

    dispatcher.update.middleware.register(DatabaseMiddleware())
    dispatcher.update.middleware.register(UserMiddleware())
    dispatcher.update.middleware.register(ServiceMiddleware())

    dispatcher.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dispatcher.errors.register(
        on_unregistered_dialog,
        ExceptionTypeFilter(UnregisteredDialogError),
    )

    setup_dialogs(dispatcher)
    try:
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), default=DefaultBotProperties(parse_mode='HTML'))
        await dispatcher.start_polling(bot)
    except (TokenValidationError, TelegramUnauthorizedError):
        logger.error("Telegram API токен в .env некорректен (TELEGRAM_BOT_TOKEN)")
