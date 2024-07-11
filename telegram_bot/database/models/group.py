from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from telegram_bot.database import Database


class StudentGroup(Database.BASE):
    __tablename__ = 'student_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    users = relationship("User", back_populates="group")