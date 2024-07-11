from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, DeclarativeBase

from telegram_bot.utils import SingletonMeta


class Database(metaclass=SingletonMeta):
    BASE: DeclarativeBase = declarative_base()

    def __init__(self):
        self.__engine = create_async_engine('sqlite+aiosqlite:///telegram_bot/database/bot_data.db')
        self.__async_session = async_sessionmaker(bind=self.__engine, class_=AsyncSession, expire_on_commit=False)

    @property
    def engine(self):
        return self.__engine

    async def get_session(self) -> AsyncSession:
        return self.__async_session()

    async def create_all(self):
        async with self.__engine.begin() as connection:
            await connection.run_sync(self.BASE.metadata.create_all)

    async def __aenter__(self):
        self.session = await self.get_session()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
