from datetime import datetime
from typing import Optional, Sequence

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot.database import Task
from telegram_bot.database.models import User, UserProgress, StudentGroup


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
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

    async def add_user_progress(self, user_id: int, task: Task):
        user_progress = UserProgress(user_id=user_id, task_id=task.id, started_at=datetime.now())
        self.session.add(user_progress)
        await self.session.commit()

    async def update_user_progress(self, user_id: int, task: Task, is_completed: bool = False):
        user_progress_query = await self.session.execute(
            select(UserProgress).filter(UserProgress.user_id == user_id, UserProgress.task_id == task.id)
        )
        try:
            user_progress: UserProgress = user_progress_query.scalar_one_or_none()
        except MultipleResultsFound:
            logger.error(f"Пользователь пытается решить одно и то же задание дважды, user: {user_id}, task: {task.id}")
            return None
        if not user_progress:
            logger.error(f"Не существует прогресс данного пользователя, user: {user_id}, task: {task.id}")
            return None
        user_progress.is_completed = is_completed
        user_progress.score = task.points
        user_progress.completed_at = datetime.now()
        user_progress.response_time = (user_progress.completed_at - user_progress.started_at).total_seconds()
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
