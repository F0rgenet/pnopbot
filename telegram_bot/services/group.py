from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot.database.models import StudentGroup


class GroupService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_group(self, name: str) -> StudentGroup:
        group = StudentGroup(name=name)
        self.session.add(group)
        await self.session.commit()
        return group

    async def get_group(self, group_id: int) -> StudentGroup:
        result = await self.session.execute(select(StudentGroup).filter(StudentGroup.id == group_id))
        return result.scalar_one_or_none()

    async def get_groups(self) -> List[StudentGroup]:
        result = await self.session.execute(select(StudentGroup))
        return result.scalars().all()

