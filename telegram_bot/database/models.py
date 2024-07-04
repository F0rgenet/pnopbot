from sqlalchemy import Column, Integer, String, Boolean
from loguru import logger

from . import Database


class User(Database.BASE):
    __tablename__ = "users"
    telegram_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    username = Column(String)
    fullname = Column(String)
    is_verified = Column(Boolean, default=False)
    privacy_consent = Column(Boolean, default=False)
    solved = Column(Integer, default=0)


class Task(Database.BASE):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    image_path = Column(String)
    answers = Column(String)
    correct_answer_index = Column(Integer)


async def register_models():
    logger.info("Регистрация моделей базы данных...")
    await Database().create_all()
    logger.success("Модели базы данных зарегистрированы")
