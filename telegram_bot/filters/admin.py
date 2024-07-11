from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from telegram_bot.database import User


def is_admin(data: Dict, widget: Whenable, manager: DialogManager):
    user: User = manager.middleware_data.get("user")
    if not user:
        return False
    return user.is_admin


def is_not_admin(data: Dict, widget: Whenable, manager: DialogManager):
    user: User = manager.middleware_data.get("user")
    if not user:
        return False
    return not user.is_admin
