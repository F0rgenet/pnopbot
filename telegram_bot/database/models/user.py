from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from telegram_bot.database import Database


class User(Database.BASE):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    full_name = Column(String(100), default="")
    is_verified = Column(Boolean, default=False)
    privacy_consent = Column(Boolean, default=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    total_points = Column(Integer, default=0) # TODO: Переименовать в total_score
    rank = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)

    user_progress = relationship("UserProgress", back_populates="user", lazy="selectin")
    achievements = relationship("UserAchievement", back_populates="user", lazy="selectin")

    group_id = Column(Integer, ForeignKey("student_groups.id"))
    group = relationship("StudentGroup", back_populates="users", lazy="selectin")


class UserProgress(Database.BASE):
    __tablename__ = 'user_progress'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    is_completed = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True))
    response_time = Column(Integer)  # в секундах

    user = relationship("User", back_populates="user_progress")
    task = relationship("Task", back_populates="user_progress")
