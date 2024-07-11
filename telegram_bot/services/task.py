from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from telegram_bot.database.models import Task, Category


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, **kwargs):
        task = Task(**kwargs)
        self.session.add(task)
        await self.session.commit()
        return task

    async def get_task(self, task_id: int):
        result = await self.session.execute(select(Task).options(joinedload(Task.options)).filter(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_tasks(self, category: Optional[str] = None):
        query = select(Task).options(joinedload(Task.options))
        if category:
            query = query.join(Task.categories).filter(Category.name == category)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_task(self, task_id: int, **kwargs):
        task = await self.get_task(task_id)
        for key, value in kwargs.items():
            setattr(task, key, value)
        await self.session.commit()
        return task

    async def delete_task(self, task_id: int):
        task = await self.get_task(task_id)
        await self.session.delete(task)
        await self.session.commit()
