from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Back, Cancel, Button, Checkbox, Next, Url
from aiogram_dialog.widgets.text import Const, Text
from aiogram_dialog import DialogManager

from telegram_bot.dialogs.states import Menu


async def on_home_button_click(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.current_context().state in Menu:
        await dialog_manager.switch_to(Menu.MAIN)
    else:
        await dialog_manager.done()


def checkbox(unchecked_text: Text, checked_text: Text, checkbox_id: str, on_click: Any | None = None,
             default: bool = False):
    unchecked_text = "◻️" + unchecked_text
    checked_text = "✅" + checked_text
    return Checkbox(unchecked_text=unchecked_text, checked_text=checked_text,
                    id=checkbox_id, on_click=on_click, default=default)


back_button = Back(Const("◀️Назад"), id="back_button")
next_button = Next(Const("▶️Далее"), id="next_button")
home_button = Button(Const("🏠Вернуться"), id="home_button", on_click=on_home_button_click)
admin_button = Url(id="report_issue", text=Const("🆘Помощь"), url=Const("t.me/forgenet"))