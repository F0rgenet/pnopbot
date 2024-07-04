from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from loguru import logger

from telegram_bot.database import User


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, telegram_id: int, username: str = None, fullname: str = None,
                          is_verified: bool = False, privacy_consent: bool = False) -> User:
        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                fullname=fullname,
                is_verified=is_verified,
                privacy_consent=privacy_consent
            )
            self.db_session.add(user)
            await self.db_session.commit()
            logger.info(f"Создан пользователь с telegram_id: {telegram_id}")
            return user
        except IntegrityError:
            await self.db_session.rollback()
            logger.error(f"Пользователь с telegram_id {telegram_id} уже существует")
            return await self.get_user(telegram_id)

    async def get_user(self, telegram_id: int) -> User:
        result = await self.db_session.execute(select(User).filter(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"Пользователь с telegram_id {telegram_id} не найден")
        return user

    async def get_or_create_user(self, telegram_id: int, username: str = None, fullname: str = None,
                                 is_verified: bool = False, privacy_consent: bool = False) -> User:
        result = await self.db_session.execute(select(User).filter(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            created_user = await self.create_user(telegram_id, username, fullname, is_verified, privacy_consent)
            return created_user
        return user

    async def get_all_users(self) -> Sequence[User]:
        result = await self.db_session.execute(select(User))
        return result.scalars().all()

    async def update_user(self, telegram_id: int, **kwargs) -> User:
        user = await self.get_user(telegram_id)
        if not user:
            logger.error(f"Невозможно обновить: Пользователь с telegram_id {telegram_id} не найден")
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        await self.db_session.commit()
        logger.info(f"Обновлен пользователь с telegram_id: {telegram_id}")
        return user

    async def delete_user(self, telegram_id: int) -> bool:
        user = await self.get_user(telegram_id)
        if not user:
            logger.error(f"Невозможно удалить: Пользователь с telegram_id {telegram_id} не найден")
            return False

        await self.db_session.delete(user)
        await self.db_session.commit()
        logger.info(f"Удален пользователь с telegram_id: {telegram_id}")
        return True
