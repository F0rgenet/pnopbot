from typing import Optional, List, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from telegram_bot.database import Task
from telegram_bot.database.models import User, UserProgress, StudentGroup


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, telegram_id: int, username: Optional[str] = None,
                                 full_name: Optional[str] = None) -> User:
        result = await self.session.execute(select(User).filter(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            self.session.add(user)
            await self.session.commit()
            logger.success(f"В базу данных добавлен пользователь {username}")
        return user

    async def get_user(self, telegram_id: int) -> User:
        result = await self.session.execute(select(User).filter(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.error(f"Пользователь {telegram_id} не был найден")
        return user

    async def get_all_users(self) -> Sequence[User]:
        result = await self.session.execute(select(User).order_by(User.total_points).filter(User.total_points > 0))
        return list(reversed(result.scalars().all()))

    async def update_user_full_name(self, user_id: int, username: str, full_name: str):
        user = await self.get_or_create_user(user_id, username)
        user.full_name = full_name
        await self.session.commit()
        logger.success(f"Обновлено ФИО пользователя {user_id}: {full_name}")

    async def update_user_privacy_consent(self, user_id: int, username: str, privacy_consent: bool):
        user = await self.get_or_create_user(user_id, username)
        user.privacy_consent = privacy_consent
        await self.session.commit()
        logger.success(f"Обновлён статус обработки персональных данных для {user_id}: {privacy_consent}")

    async def update_user_group(self, user_id: int, username: str, group: StudentGroup):
        user = await self.get_or_create_user(user_id, username)
        user.group = group
        await self.session.commit()
        logger.success(f"Обновлена группа для {user_id}: {group.name}")

    async def update_user_stats(self, user_id: int):
        user = await self.get_or_create_user(user_id)
        result = await self.session.execute(
            select(UserProgress).filter(UserProgress.user_id == user.id)
        )
        user_progress: Sequence[UserProgress] = result.scalars().all()
        logger.debug(f"Количество: {len(user_progress)}")
        user.total_points = sum(progress_item.score for progress_item in user_progress)
        user.xp = sum(progress_item.score // 4 for progress_item in user_progress)
        user.level = user.xp // 100
        await self.session.commit()
        logger.success(f"Обновлена статистика пользователя {user.full_name}")

    async def update_user_progress(self, user_id: int, task: Task, is_completed: bool = False):
        user_progress = await self.session.execute(
            select(UserProgress).filter(UserProgress.user_id == user_id, UserProgress.task_id == task.id)
        )
        user_progress = user_progress.scalar_one_or_none()
        user = await self.get_user(user_id)
        if not user_progress:
            user_progress = UserProgress(user_id=user.id, task_id=task.id)
            self.session.add(user_progress)
        user_progress.is_completed = is_completed
        user_progress.score = task.points
        user_progress.completed_at = func.now()
        await self.session.commit()
        await self.update_user_stats(user_id)
        logger.success(f"Обновлён прогресс пользователя {user_id}")
        return user_progress

    async def get_completed_tasks(self, user_id: int, only_completed_tasks: bool = False) -> Sequence[Task]:
        query = select(Task).join(UserProgress).filter(
            UserProgress.user_id == user_id
        )
        if only_completed_tasks:
            query = query.filter(UserProgress.is_completed == True)
        result = await self.session.execute(query)
        return result.scalars().all()
