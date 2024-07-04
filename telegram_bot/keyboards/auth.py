from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


def get_not_verified_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Повторить ввод", callback_data=f"fullname_input:retry")
    builder.button(text=f"Обратиться к администратору", url="t.me/forgenet")
    # TODO: Система тикетов
    return builder.as_markup()


def get_privacy_consent_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Принять", callback_data=f"privacy_consent:1")
    builder.button(text=f"Отклонить", callback_data=f"privacy_consent:0")
    return builder.as_markup()


def get_privacy_consent_rejected_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Вернуться к соглашению", callback_data=f"privacy_consent:retry")
    builder.button(text=f"Обратиться к администратору", url="t.me/forgenet")
    return builder.as_markup()


def get_auth_done_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Перейти в меню", callback_data=f"menu")
    return builder.as_markup()
