from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from telegram_bot.database import Database

task_category = Table('task_category', Database.BASE.metadata,
                      Column('task_id', Integer, ForeignKey('tasks.id')),
                      Column('category_id', Integer, ForeignKey('categories.id')))


class Task(Database.BASE):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty = Column(String(20))
    points = Column(Integer, default=0) # TODO: Переименовать в score
    media_path = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    type_id = Column(Integer, ForeignKey("task_types.id"))
    type = relationship("TaskType", back_populates="tasks", lazy="selectin")

    options = relationship("Option", back_populates="task", lazy="selectin")
    categories = relationship("Category", secondary=task_category, back_populates="tasks", lazy="selectin")
    user_progress = relationship("UserProgress", back_populates="task", lazy="selectin")


class TaskType(Database.BASE):
    __tablename__ = 'task_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    tasks = relationship("Task", back_populates="type", lazy="selectin")


class Category(Database.BASE):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

    tasks = relationship("Task", secondary=task_category, back_populates="categories", lazy="selectin")


class Option(Database.BASE):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    task = relationship("Task", back_populates="options", lazy="selectin")
