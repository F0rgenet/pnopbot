from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from telegram_bot.database import User


def is_verified(data: Dict, widget: Whenable, manager: DialogManager):
    user: User = manager.middleware_data.get("user")
    if not user:
        return False
    return user.full_name and user.privacy_consent and user.group


def is_not_verified(data: Dict, widget: Whenable, manager: DialogManager):
    user: User = manager.middleware_data.get("user")
    if not user:
        return False
    return not (user.full_name and user.privacy_consent and user.group)
