from aiogram.fsm.state import State, StatesGroup


class Auth(StatesGroup):
    FULLNAME_INPUT = State()
    FULLNAME_INVALID = State()
    PRIVACY_CONSENT_REQUIRE = State()
    PRIVACY_CONSENT_CANCELED = State()
    GROUP_SELECT = State()


class Menu(StatesGroup):
    MAIN = State()
    PROFILE = State()
    ANSWERS_HISTORY = State()
    LEADERBOARD = State()


class Settings(StatesGroup):
    MAIN = State()


class Tasks(StatesGroup):
    CATEGORY_SELECT = State()
    TASK_SELECT = State()
    TASK_ACTIVE = State()
    TASK_DONE = State()
    RESULT_VIEW = State()


class Admin(StatesGroup):
    MAIN = State()
    MANAGE_TASKS = State()
    MANAGE_CATEGORIES = State()
    MANAGE_USERS = State()
