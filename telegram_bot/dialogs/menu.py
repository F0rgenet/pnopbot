from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import SwitchTo, Group, Row, Start, Button
from aiogram_dialog.widgets.text import Const, Format

from telegram_bot.database import User, StudentGroup
from telegram_bot.dialogs.states import Tasks, Menu, Settings, Auth
from telegram_bot.filters.auth import is_verified, is_not_verified
from telegram_bot.services import UserService
from telegram_bot.utils.dialog_constants import home_button, back_button


async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    user: User = dialog_manager.middleware_data["user"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]

    await user_service.update_user_stats(user.id)

    user_rank_text = f"{user.rank}" if user.rank else "-"
    group: StudentGroup = user.group

    completed_tasks = len(await user_service.get_completed_tasks(user.id, False))
    correct_answers = len(await user_service.get_completed_tasks(user.id, True))

    if not group:
        group_name = "-"
    else:
        group_name = group.name

    return {
        "full_name": user.full_name,
        "group": group_name,
        "level": user.level,
        "current_xp": user.xp,
        "next_level_xp": user.level * 100,
        "score": user.total_points,
        "leaderboard_position": user_rank_text,
        "completed_tasks": completed_tasks,
        "correct_answers": correct_answers,
        "average_answer_time": 0
    }


async def get_leaderboard_data(dialog_manager: DialogManager, **kwargs):
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    users = await user_service.get_all_users()
    result = "Пользователь | Количество очков\n"
    table = []
    for user in users:
        table.append(f"{user.full_name} {user.total_points}")
    return {"leaderboard": result + "\n".join(table)}


async def auth_clicked(cq: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=Auth.FULLNAME_INPUT, mode=StartMode.RESET_STACK)


menu_dialog = Dialog(
    Window(
        Const("Готовы прокачать свои навыки работы с Microsoft Office? Выбирайте раздел и начинайте!\n"
              "Что вас интересует? 👇\n"
              "🚀 Решать задания: проверьте свои знания и получите новую порцию полезной информации!\n"
              "👤 Профиль: отслеживайте свой прогресс, достижения и историю ответов.\n"
              "🏆 Рейтинг: узнайте, кто в топе, и сравните свои результаты с другими участниками.\n"
              "⚙️ Настройки: настройте бота под себя: выберите темы, сложность заданий и получайте уведомления.\n",
              when=is_verified),
        Group(
            Start(
                Const("🚀Решать задания"),
                id="solve_tasks_button",
                state=Tasks.CATEGORY_SELECT,
            ),
            Row(
                SwitchTo(
                    Const("👤Профиль"),
                    id="profile_button",
                    state=Menu.PROFILE
                ),
                SwitchTo(
                    Const("🏆Рейтинг"),
                    id="leaderboard_button",
                    state=Menu.LEADERBOARD
                ),
                Start(
                    Const("⚙️Настройки"),
                    id="settings_button",
                    state=Settings.MAIN
                )
            ),

            when=is_verified,
        ),
        Button(Const("🔓Авторизоваться"), id="auth_button", when=is_not_verified, on_click=auth_clicked),
        state=Menu.MAIN,
    ),

    Window(
        Const("<b>Ваш профиль:</b>"),
        Format("ФИО: {full_name}"),
        Format("Группа: {group}"),

        Const("\n<b>Прогресс</b>"),
        Format("🏆 Уровень: <code>{level}</code> (<code>{current_xp}</code>/<code>{next_level_xp}</code> XP)"),
        Format("⭐ Баллы: <code>{score}</code>"),
        Format("🥇 Место в рейтинге: <code>{leaderboard_position}</code>"),
        Const("\n<b>Статистика:</b>"),
        Format("📝 Выполнено заданий: <code>{completed_tasks}</code>"),
        Format("🎯 Правильных ответов: <code>{correct_answers}</code>"),
        Format("⏳ Среднее время ответа: <code>{average_answer_time}</code> сек."),
        Const("\n<b>Достижения:</b>"),
        Format("Список достижений пользователя с иконками, например:\n🥇 Знаток Word, 🚀 Быстрый ум"),
        SwitchTo(text=Const("🗂️История ответов"), id="answer_history",
                 state=Menu.ANSWERS_HISTORY),
        home_button,
        getter=get_profile_data,
        state=Menu.PROFILE
    ),

    Window(
        Const("История ответов ещё не реализована..."),
        back_button,
        state=Menu.ANSWERS_HISTORY
    ),

    Window(
        Const("Таблица лидеров:"),
        Format("{leaderboard}"),
        home_button,
        getter=get_leaderboard_data,
        state=Menu.LEADERBOARD
    )
)
