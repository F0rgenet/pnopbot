from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent, Message, ReplyKeyboardRemove

from aiogram_dialog import DialogManager, setup_dialogs, ShowMode, StartMode
from aiogram_dialog.api.exceptions import NoContextError
from loguru import logger

from telegram_bot.dialogs.states import Menu


async def process_error(error_message: str, event: ErrorEvent, dialog_manager: DialogManager):
    logger.error(f"Возникла ошибка: {event.exception}")

    return_to_menu = not dialog_manager.has_context()

    error_message += "\nПеренаправление в главное меню..." if return_to_menu else ""

    if event.update.callback_query:
        await event.update.callback_query.answer(error_message)
        if event.update.callback_query.message and return_to_menu:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass
    elif event.update.message:
        await event.update.message.answer(error_message)
    if return_to_menu:
        try:
            await dialog_manager.start(
                Menu.MAIN,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.SEND,
            )
        except TelegramBadRequest:
            logger.warning("Не удалось перезапустить меню")


async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager):
    error_message = "Контекст сообщения недоступен."
    await process_error(error_message, event, dialog_manager)


async def on_unregistered_dialog(event: ErrorEvent, dialog_manager: DialogManager):
    error_message = "В связи с техническим обслуживанием данный раздел недоступен"
    await process_error(error_message, event, dialog_manager)