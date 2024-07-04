from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from telegram_bot.database import Task


class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_task(self, title: str, description: str = None, image_path: str = None) -> Task:
        task = Task(
            title=title,
            description=description,
            image_path=image_path
        )
        self.db_session.add(task)
        await self.db_session.commit()
        logger.info(f"Создана задача с id: {task.task_id}")
        return task

    async def get_task(self, task_id: int) -> Task:
        result = await self.db_session.execute(select(Task).filter(Task.task_id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            logger.warning(f"Задача с id {task_id} не найдена")
        return task

    async def get_all_tasks(self) -> Sequence[Task]:
        result = await self.db_session.execute(select(Task))
        return result.scalars().all()

    async def update_task(self, task_id: int, **kwargs) -> Task:
        task = await self.get_task(task_id)
        if not task:
            logger.error(f"Невозможно обновить: Задача с id {task_id} не найдена")
            return None

        for key, value in kwargs.items():
            setattr(task, key, value)

        await self.db_session.commit()
        logger.info(f"Обновлена задача с id: {task_id}")
        return task

    async def delete_task(self, task_id: int) -> bool:
        task = await self.get_task(task_id)
        if not task:
            logger.error(f"Невозможно удалить: Задача с id {task_id} не найдена")
            return False

        await self.db_session.delete(task)
        await self.db_session.commit()
        logger.info(f"Удалена задача с id: {task_id}")
        return True