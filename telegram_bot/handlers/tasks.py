from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart

import random

from telegram_bot.services import TaskService, UserService
from telegram_bot.database import Database
from telegram_bot.keyboards.user import *
from telegram_bot.keyboards.task import *
from telegram_bot.states import Tasks

from .auth import require_privacy_consent, require_fullname

router = Router()


@router.message(F.text == MenuButton.TESTS.value)
async def test(message: Message, state: FSMContext):
    await state.set_state(Tasks.solve)
    await message.answer("Вы начали проходить тест", reply_markup=get_back_keyboard())
    await show_question(message, (await get_questions())[1], state)


async def get_questions():
    async with Database() as session:
        task_service = TaskService(session)
        result = await task_service.get_all_tasks()
        random.shuffle(result)
    return result


async def show_question(message: Message, question: Task, state: FSMContext):
    await state.set_data({"right_answer": question.answers.split(";")[question.correct_answer_index]})
    keyboard = generate_task_keyboard(question)
    photo = FSInputFile(f"data/task_images/{question.image_path}")
    await message.answer_photo(photo=photo, caption=f"<b>{question.title}</b>\n{question.description}",
                               reply_markup=keyboard)


@router.callback_query(F.data == "test:correct_answer", Tasks.solve)
async def got_correct_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    right_answer = (await state.get_data())["right_answer"]
    await callback.message.edit_caption(caption=callback.message.caption + f"\nВерно!\nОтвет: {right_answer}")
    async with Database() as session:
        user_service = UserService(session)
        user_id = callback.from_user.id
        solved = (await user_service.get_user(user_id)).solved
        await user_service.update_user(user_id, solved=solved + 1)
    await show_question(callback.message, (await get_questions())[1], state)


@router.callback_query(F.data == "test:wrong_answer", Tasks.solve)
async def got_wrong_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    right_answer = (await state.get_data())["right_answer"]
    await callback.message.edit_caption(caption=callback.message.caption + f"\nНеверно :(\nПравильный ответ был: {right_answer}")
    await show_question(callback.message, (await get_questions())[1], state)