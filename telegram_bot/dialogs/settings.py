from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const

from telegram_bot.dialogs.states import Settings
from telegram_bot.utils.dialog_constants import checkbox, home_button

settings_dialog = Dialog(
    Window(
        Const("Настройки"),
        checkbox(Const("Отображение в рейтинге"), Const("Отображение в рейтинге"),
                 "leaderboard_show_setting"),
        home_button,
        state=Settings.MAIN
    )
)
