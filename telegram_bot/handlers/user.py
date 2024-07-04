from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart


from telegram_bot.services import UserService
from telegram_bot.database import Database
from telegram_bot.keyboards.user import *
from telegram_bot.keyboards.task import *
from telegram_bot.handlers.tasks import get_questions

from .auth import require_privacy_consent, require_fullname

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    async with Database() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create_user(message.from_user.id, message.from_user.username)
        if not user.fullname:
            await require_fullname(message, state)
        elif not user.privacy_consent:
            await require_privacy_consent(message, state)
        else:
            await menu(message, state)


async def menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Меню", reply_markup=get_menu_keyboard())


@router.callback_query(F.data == "menu")
async def redirect_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await menu(callback.message, state)


@router.message(F.text == MenuButton.PROFILE.value)
async def profile(message: Message, state: FSMContext):
    async with Database() as session:
        user_service = UserService(session)
        user_id = message.from_user.id
        solved = (await user_service.get_user(user_id)).solved
    await message.answer(f"Заданий, решённых верно: {solved}")


@router.message(F.text == MenuButton.LEADERBOARD.value)
async def leaderboard(message: Message, state: FSMContext):
    await message.answer("Лидерборд:")


@router.message(F.text == MenuButton.SETTINGS.value)
async def settings(message: Message, state: FSMContext):
    await message.answer("Настройки:")


@router.message(F.text == MenuButton.BACK.value)
async def profile(message: Message, state: FSMContext):
    await start(message, state)