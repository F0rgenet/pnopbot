import os

from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.token import TokenValidationError
from aiogram.exceptions import TelegramUnauthorizedError

from telegram_bot.database import register_models
from .handlers import router as handlers_router

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), default=DefaultBotProperties(parse_mode='HTML'))


async def on_startup(dispatcher: Dispatcher):
    await register_models()
    dispatcher.include_router(handlers_router)
    logger.success("Бот запущен")


async def on_shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    logger.success("Бот остановлен")


async def startup():
    logger.info("Запуск бота...")
    fsm_storage = MemoryStorage()
    dispatcher = Dispatcher(storage=fsm_storage)
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)
    try:
        await dispatcher.start_polling(bot)
    except (TokenValidationError, TelegramUnauthorizedError):
        logger.error("Telegram API токен в .env некорректен (TELEGRAM_BOT_TOKEN)")
