from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from telegram_bot.database import Database


class Achievement(Database.BASE):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))

    users = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Database.BASE):
    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    achievement_id = Column(Integer, ForeignKey('achievements.id'))
    achieved_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")
