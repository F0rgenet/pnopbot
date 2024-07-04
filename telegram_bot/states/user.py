from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class Auth(StatesGroup):
    fullname = State()
    privacy_consent = State()


class Tasks(StatesGroup):
    prepare = State()
    solve = State()
    result = State()
