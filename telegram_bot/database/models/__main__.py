from loguru import logger
from telegram_bot.database import Database


async def register_models():
    logger.info("Регистрация моделей базы данных...")
    try:
        await Database().create_all()
    except Exception as e:
        logger.exception(f"Ошибка при регистрации моделей базы данных: {e}")
    logger.success("Модели базы данных зарегистрированы")


async def dispose_database():
    logger.info("Закрытие соединения с базой данных...")
    try:
        await Database().engine.dispose()
        logger.success("Соединение с базой данных успешно закрыто")
    except Exception as e:
        logger.exception(f"Ошибка при закрытии соединения с базой данных: {e}")