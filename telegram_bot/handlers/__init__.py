from aiogram import Router

from .main import router as main_router
from telegram_bot.dialogs.menu import menu_dialog
from telegram_bot.dialogs.tasks import tasks_dialog
from telegram_bot.dialogs.settings import settings_dialog
from telegram_bot.dialogs.auth import auth_dialog

router = Router()

router.include_router(main_router)

router.include_router(menu_dialog)
router.include_router(settings_dialog)
router.include_router(tasks_dialog)
router.include_router(auth_dialog)
