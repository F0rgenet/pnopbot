from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Cancel, Input, Button, Select
from aiogram_dialog.manager import StartMode

from telegram_bot.states.user import Auth
from telegram_bot.services import UserService
from telegram_bot.database import Database
from telegram_bot.utils.validators import validate_name, verify_user
from telegram_bot.dialog import Dialog
from telegram_bot.keyboards.auth import *

db = Database()


class AuthDialog(Dialog):
    async def fullname_step(self, m):
        widget = Input(validate=validate_name, field_name="fullname", label="Введите своё имя и фамилию:")
        await widget(m)

    async def choose_group_step(self, m):
        widget = Select(
            items=["Группа 1", "Группа 2", "Группа 3", "Группа 4"],
            label="Выберите ваш номер учебной группы:"
        )
        await widget(m)

    async def privacy_consent_step(self, m):
        privacy_consent_document = FSInputFile("data/privacy_consent.pdf",
                                               filename="Согласие на обработку персональных данных.pdf")
        await m.answer_document(
            caption="Для использования бота, подтвердите своё согласие на обработку персональных данных.",
            document=privacy_consent_document,
            reply_markup=get_privacy_consent_keyboard()
        )

    async def _on_closed(self, m):
        await m.answer("Вы завершили авторизацию.")


dialog_manager = DialogManager(AuthDialog())


@dispatcher.message_handler(Text(equals="auth_start"), state="*")
async def start_authentication(m: types.Message, state: FSMContext):
    await dialog_manager.start(m, StartMode.NOW)


@dispatcher.message_handler(state=Auth.fullname)
async def handle_fullname(m: types.Message, state: FSMContext):
    user_data = await db.get_user_data(m.from_user.id)
    fullname = m.text.strip()

    if not validate_name(fullname.title()):
        await m.answer("Пожалуйста, введите корректное имя и фамилию.")
        return

    user_data["full_name"] = fullname.title()
    await dialog_manager.advance(m, Auth.choose_group)


@dispatcher.message_handler(state=Auth.choose_group)
async def handle_choose_group(m: types.Message, state: FSMContext):
    group_number = m.text

    if group_number not in ["Группа 1", "Группа 2", "Группа 3", "Группа 4"]:
        await m.answer("Пожалуйста, выберите номер из предложенных вариантов.")
        return

    user_data = await db.get_user_data(m.from_user.id)
    user_data["group"] = group_number
    await dialog_manager.advance(m, Auth.privacy_consent)