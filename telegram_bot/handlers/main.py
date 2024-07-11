from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import CommandStart
from loguru import logger

from aiogram_dialog import DialogManager, setup_dialogs, ShowMode, StartMode

from telegram_bot.dialogs import states
from telegram_bot.database import User

router = Router()


@router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    logger.info(f"Пользователь {message.from_user.username} начал диалог с ботом")
    user: User = dialog_manager.middleware_data["user"]
    if not user.full_name:
        await dialog_manager.start(states.Auth.FULLNAME_INPUT, mode=StartMode.RESET_STACK)
    elif not user.privacy_consent:
        await dialog_manager.start(states.Auth.PRIVACY_CONSENT_REQUIRE, mode=StartMode.RESET_STACK)
    elif not user.group:
        await dialog_manager.start(states.Auth.GROUP_SELECT, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(states.Menu.MAIN, mode=StartMode.RESET_STACK)
