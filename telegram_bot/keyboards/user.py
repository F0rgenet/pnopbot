from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton

from enum import Enum


class MenuButton(Enum):
    TESTS = "🧑‍💻Проходить тесты"
    PROFILE = "👤Профиль"
    LEADERBOARD = "🏆Таблица лидеров"
    SETTINGS = "⚙️Настройки"
    BACK = "◀️Назад"


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=MenuButton.TESTS.value),
    )
    builder.row(
        KeyboardButton(text=MenuButton.PROFILE.value),
        KeyboardButton(text=MenuButton.LEADERBOARD.value),
        KeyboardButton(text=MenuButton.SETTINGS.value),
    )
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие")


def get_back_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=MenuButton.BACK.value)
    return builder.as_markup(resize_keyboard=True)
