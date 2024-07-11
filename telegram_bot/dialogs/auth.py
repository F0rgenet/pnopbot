import operator

import aiofiles
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Group, Button, Checkbox, Select
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger

from telegram_bot.dialogs.states import Auth, Menu
from telegram_bot.services import GroupService
from telegram_bot.services.user import UserService
from telegram_bot.utils.dialog_constants import checkbox, next_button, admin_button
from telegram_bot.utils.validators import validate_full_name


async def on_full_name_enter(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    full_name = message.text.title()
    if not validate_full_name(full_name):
        await message.answer("Введите <b>корректное</b> ФИО по образцу: <code>Иванов Кирилл Романович</code>")
        return

    async with aiofiles.open("data/students.txt", "r", encoding="utf-8") as students_list:
        students = (await students_list.read()).split("\n")
        if full_name not in students:
            logger.info(f"Пользователь не был найден в списке студентов: {full_name}")
            await dialog_manager.switch_to(state=Auth.FULLNAME_INVALID)
            return

    user_service: UserService = dialog_manager.middleware_data['user_service']
    await user_service.update_user_full_name(message.from_user.id, message.from_user.username, full_name)

    await dialog_manager.switch_to(state=Auth.PRIVACY_CONSENT_REQUIRE)


async def get_privacy_consent_checkbox_hint(dialog_manager: DialogManager, **kwargs):
    return {"checkbox_hint": "согласны" if dialog_manager.dialog_data.get("privacy_consent_checkbox") else "НЕ согласны"}


async def on_privacy_consent_checkbox(callback: CallbackQuery, target_checkbox: Checkbox,
                                      dialog_manager: DialogManager):
    dialog_manager.dialog_data["privacy_consent_checkbox"] = not target_checkbox.is_checked()


async def on_privacy_consent_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    checkbox_state = dialog_manager.dialog_data.get("privacy_consent_checkbox")
    if not checkbox_state:
        await dialog_manager.switch_to(state=Auth.PRIVACY_CONSENT_CANCELED)
    else:
        user_service: UserService = dialog_manager.middleware_data['user_service']
        await user_service.update_user_privacy_consent(callback.from_user.id, callback.from_user.username,
                                                       True)
        await dialog_manager.switch_to(state=Auth.GROUP_SELECT)


async def get_groups_data(dialog_manager: DialogManager, **kwargs):
    group_service: GroupService = dialog_manager.middleware_data['group_service']
    groups = [(group.name, group.id) for group in await group_service.get_groups()]
    selected_group_id = dialog_manager.dialog_data.get("selected_group_id")
    if selected_group_id:
        selected_group_name = (await group_service.get_group(selected_group_id)).name
    else:
        selected_group_name = "-"
    return {"group_buttons": groups, "selected_group": selected_group_name}


async def on_group_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["selected_group_id"] = item_id


async def on_group_selection_done(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    selected_group_id = dialog_manager.dialog_data.get("selected_group_id")
    if not selected_group_id:
        return await callback.answer("Сначала выберите свою группу", show_alert=True)
    group_service: GroupService = dialog_manager.middleware_data['group_service']
    user_service: UserService = dialog_manager.middleware_data['user_service']
    selected_group = await group_service.get_group(selected_group_id)
    await user_service.update_user_group(callback.from_user.id, callback.from_user.username, selected_group)
    await dialog_manager.start(state=Menu.MAIN, mode=StartMode.RESET_STACK)


auth_dialog = Dialog(
    Window(
        Const("Приветствуем в <b>Пнопбот</b>! 👋"),
        Const("Чтобы начать, пожалуйста, введите ФИО."),
        Const("\nНапример: <code>Иванов Кирилл Романович</code>"),
        Const("Это поможет нам правильно обращаться к вам и отслеживать ваши успехи! 🤓 "),
        MessageInput(on_full_name_enter),
        state=Auth.FULLNAME_INPUT
    ),
    Window(
        Const("🤔 Хмм, кажется, ваших данных ещё нет в нашей системе."),
        Const("Пожалуйста, убедитесь, что вы ввели ФИО полностью и без ошибок."),
        Const("Если вы уверены, что всё верно, обратитесь к администратору для добавления вас в базу данных бота "
              "(кнопка <b>🆘Помощь</b>)."),
        Group(
            SwitchTo(id="repeat_fullname_input", text=Const("🔄Повторить ввод"), state=Auth.FULLNAME_INPUT),
            admin_button,
            width=2
        ),
        state=Auth.FULLNAME_INVALID
    ),
    Window(
        StaticMedia(path="data/Политика конфиденциальности.pdf", type=ContentType.DOCUMENT),
        Const("🔒 Мы гарантируем конфиденциальность и защиту ваших персональных данных."),
        Const("✅ Нажимая кнопку 'Согласен', вы подтверждаете свое согласие на обработку ") +
        Const("персональных данных в соответствии с политикой конфиденциальности."),
        Format("Сейчас вы <b>{checkbox_hint}</b> с политикой конфиденциальности."),
        checkbox(Const("Согласен"), Const("Согласен"), "privacy_consent_checkbox",
                 on_click=on_privacy_consent_checkbox),
        Button(next_button.text, id="privacy_consent_next", on_click=on_privacy_consent_next),
        state=Auth.PRIVACY_CONSENT_REQUIRE,
        getter=get_privacy_consent_checkbox_hint
    ),
    Window(
        Const("Очень жаль, что вы не согласны с политикой конфиденциальности."),
        Const("Без вашего согласия я не могу продолжить работу. 😓"),
        Const("Вы можете пересмотреть своё решение или обратиться к администратору."),
        SwitchTo(id="repeat_privacy_consent", text=Const("🔄Изменить выбор"), state=Auth.PRIVACY_CONSENT_REQUIRE),
        admin_button,
        state=Auth.PRIVACY_CONSENT_CANCELED
    ),
    Window(
        Const("Выберите группу, в которой вы обучаетесь! 🧷"),
        Format("Выбрана группа: <b>{selected_group}</b>"),
        Group(Select(
            Format("{item[0]}"),
            id="groups_select",
            item_id_getter=operator.itemgetter(1),
            items="group_buttons",
            on_click=on_group_selected
        ), id="groups_divider", width=3),
        Button(Const("Завершить"), id="group_select_done", on_click=on_group_selection_done),
        state=Auth.GROUP_SELECT,
        getter=get_groups_data
    )
)
