from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot.database.models import Category, Task


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_category(self, name: str, description: Optional[str] = None):
        category = Category(name=name, description=description)
        self.session.add(category)
        await self.session.commit()
        return category

    async def get_category(self, category_id: int):
        result = await self.session.execute(select(Category).filter(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_categories(self):
        result = await self.session.execute(select(Category))
        return result.scalars().all()

    async def get_category_tasks(self, category_id: int):
        result = await self.session.execute(select(Task).where(Task.categories.any(Category.id == category_id)))
        return result.scalars().all()
