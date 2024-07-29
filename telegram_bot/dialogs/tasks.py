import random
import operator
import queue

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Group, Select, Button, Radio, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from telegram_bot.database import Task
from telegram_bot.dialogs.states import Tasks
from telegram_bot.services import CategoryService, UserService
from telegram_bot.utils.dialog_constants import home_button


async def get_categories_data(dialog_manager: DialogManager, **kwargs):
    category_service: CategoryService = dialog_manager.middleware_data['category_service']
    categories = []
    for category in await category_service.get_categories():
        categories.append((category.name, category.id, len(await category_service.get_category_tasks(category.id))))

    selected_category_id = dialog_manager.dialog_data.get("selected_category_id")
    if selected_category_id:
        selected_category_name = (await category_service.get_category(selected_category_id)).name
    else:
        selected_category_name = "-"
    return {"categories": categories, "selected_category": selected_category_name}


async def on_category_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["selected_category_id"] = item_id


async def on_category_selection_done(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    selected_category_id = dialog_manager.dialog_data.get("selected_category_id")
    if not selected_category_id:
        return await callback.answer("Сначала выберите категорию заданий", show_alert=True)
    category_service: CategoryService = dialog_manager.middleware_data.get('category_service')
    tasks_queue = queue.Queue()
    for task in await category_service.get_category_tasks(selected_category_id):
        tasks_queue.put(task)
    dialog_manager.dialog_data["selected_tasks_queue"] = tasks_queue
    dialog_manager.dialog_data["answers"] = []
    dialog_manager.dialog_data["current_user_id"] = callback.from_user.id
    await dialog_manager.switch_to(state=Tasks.TASK_ACTIVE)


async def get_next_task(dialog_manager: DialogManager, **kwargs):
    tasks_queue: queue.Queue = dialog_manager.dialog_data.get("selected_tasks_queue")
    current_task: Task = tasks_queue.get()
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    if not current_task:
        return await dialog_manager.done()
    dialog_manager.dialog_data["current_task"] = current_task
    dialog_manager.dialog_data["current_answer_response"] = "❌Неверно"
    options = [(option.content, option.id) for option in current_task.options]
    random.shuffle(options)
    tasks_queue.task_done()
    user_id = dialog_manager.dialog_data["current_user_id"]
    await user_service.add_user_progress(user_id, current_task)
    return {"task": current_task, "options": options}


async def on_answer_selected(callback: CallbackQuery, widget: Radio, dialog_manager: DialogManager, item_id: str):
    await dialog_manager.switch_to(state=Tasks.TASK_DONE)
    task: Task = dialog_manager.dialog_data["current_task"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]

    selected_option = next(option for option in task.options if option.id == int(item_id))
    is_correct = selected_option.is_correct

    if is_correct:
        dialog_manager.dialog_data["current_answer_response"] = "✅Верно"
        dialog_manager.dialog_data["answers"].append(True)
        await callback.answer("Правильный ответ!")
    else:
        dialog_manager.dialog_data["answers"].append(False)
        await callback.answer("Неправильный ответ.")

    await user_service.update_user_progress(callback.from_user.id, task, is_correct)


async def get_current_task(dialog_manager: DialogManager, **kwargs):
    tasks_queue: queue.Queue = dialog_manager.dialog_data.get("selected_tasks_queue")
    remaining_count = tasks_queue.unfinished_tasks
    current_task = dialog_manager.dialog_data.get("current_task")
    current_answer_response = dialog_manager.dialog_data.get("current_answer_response")
    return {"task": current_task, "remaining_count": remaining_count, "current_answer_response": current_answer_response}


async def get_results(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data.get("answers")
    if not data:
        return {"answers": "Ответов нет..."}
    answers = [f"Задание №{i+1}) {'✅' if answer else '❌'}" for i, answer in enumerate(data)]
    return {"answers": "\n".join(answers)}


tasks_dialog = Dialog(
    Window(
        Const("Выберите категорию задания"),
        Format("Выбрана категория: <b>{selected_category}</b>"),
        Group(Select(
            Format("{item[0]} (x{item[2]})", when=F["item"][2] > 0),
            id="groups_select",
            item_id_getter=operator.itemgetter(1),
            items="categories",
            on_click=on_category_selected,
        ), id="groups_divider", width=4),
        Button(Const("❓Начать решать задания"), id="group_select_done", on_click=on_category_selection_done),
        home_button,
        getter=get_categories_data,
        state=Tasks.CATEGORY_SELECT,
    ),
    Window(
        Format("{task.title}"),
        Format("Описание: {task.description}"),
        Format("Сложность: {task.difficulty}"),
        Format("Баллы: {task.points}"),
        Group(
            Select(
                Format("{item[0]}"),
                id="answer_options",
                item_id_getter=operator.itemgetter(1),
                items="options",
                on_click=on_answer_selected,
            ),
            width=2
        ),
        home_button,
        getter=get_next_task,
        state=Tasks.TASK_ACTIVE
    ),
    Window(
        Format("{task.title}"),
        Format("Баллы: {task.points}"),
        Format("Решено:\n{current_answer_response}"),
        SwitchTo(text=Const("🔥Следующее задание"), state=Tasks.TASK_ACTIVE, id="next_task_button",
                 when=F["remaining_count"] > 0),
        SwitchTo(text=Const("🥇Результаты"), state=Tasks.RESULT_VIEW, id="results_button",
                 when=F["remaining_count"] == 0),
        home_button,
        # TODO: Кастомная кнопка
        getter=get_current_task,
        state=Tasks.TASK_DONE
    ),
    Window(
        Format("Ваши ответы:"),
        Format("{answers}"),
        home_button,
        getter=get_results,
        state=Tasks.RESULT_VIEW
    )
)
