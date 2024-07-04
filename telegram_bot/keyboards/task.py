from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from telegram_bot.database.models import Task

import random


def generate_task_keyboard(task: Task) -> InlineKeyboardMarkup:
    answers = task.answers.split(";")
    correct_answer_index = task.correct_answer_index
    answer = answers[correct_answer_index]
    builder = InlineKeyboardBuilder()
    for choice in answers:
        if choice != answer:
            builder.button(text=choice, callback_data=f"test:wrong_answer")
        else:
            builder.button(text=choice, callback_data=f"test:correct_answer")
    return builder.as_markup()
