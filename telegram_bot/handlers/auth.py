from aiogram import F, Router
from aiogram.types import Message, FSInputFile, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from loguru import logger

from telegram_bot.states.user import Auth
from telegram_bot.services import UserService
from telegram_bot.utils.validators import validate_name, verify_user
from telegram_bot.database import Database
from telegram_bot.keyboards.auth import *

router = Router()


async def require_fullname(message: Message, state: FSMContext):
    await message.answer(text="Для того, чтобы воспользоваться ботом вам необходимо авторизоваться, "
                              "введите имя и фамилию.\nПример: <code>Иван Иванов</code>\nP.S. Иван Иванов доступен",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.fullname)


@router.message(Auth.fullname)
async def got_fullname(message: Message, state: FSMContext):
    telegram_user = message.from_user
    logger.info(f"Пользователь {telegram_user.username} ввёл имя и фамилию: {message.text}")
    async with Database() as session:
        user_service = UserService(session)
        database_user = await user_service.get_user(telegram_user.id)
        if not database_user:
            return
        if database_user.fullname:
            logger.warning(f"Пользователь {telegram_user.username} уже вводил имя и фамилию")

        fullname = message.text
        if not validate_name(fullname.title()):
            logger.info(f"Пользователь {telegram_user.username} ввёл некорректные данные: {fullname.title()}")
            await message.answer("Введите корректные данные.\nПример: <code>Иван Иванов</code>",
                                 reply_markup=ReplyKeyboardRemove())
            return
        await user_service.update_user(telegram_user.id, fullname=fullname.title())

        if await verify_user(fullname.title()):
            await user_service.update_user(telegram_user.id, verified=True)
            await message.answer("Вы есть в списке студентов, аккаунт авторизован")
        else:
            await message.answer("Ваши данные не были обнаружены в списке студентов, аккаунт не может быть авторизован,"
                                 " проверьте корректность введённых данных, повторите ввод "
                                 "или обратитесь к администратору.",
                                 reply_markup=get_not_verified_keyboard())
            return

        if not database_user.privacy_consent:
            await require_privacy_consent(message, state)


@router.callback_query(F.data == "fullname_input:retry")
async def got_fullname_retry(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await require_fullname(callback.message, state)


async def require_privacy_consent(message: Message, state: FSMContext):
    privacy_consent_document = FSInputFile("data/privacy_consent.pdf",
                                           filename="Согласие на обработку персональных данных.pdf")
    await message.answer_document(
        caption="Чтобы использовать бота, подтвердите своё согласие на обработку персональных "
                "данных.\nПодтверждение: [ ]",
        document=privacy_consent_document,
        reply_markup=get_privacy_consent_keyboard())
    await state.set_state(Auth.privacy_consent)


@router.callback_query(F.data == "privacy_consent:1")
async def got_privacy_consent(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_caption(caption=callback.message.caption.replace("[ ]", "[✅]"))
    await callback.message.answer("Вы <b>приняли</b> соглашение на обработку персональных данных, теперь вы можете "
                                  "пользоваться ботом.", reply_markup=get_auth_done_keyboard())
    telegram_user = callback.from_user
    async with Database() as session:
        user_service = UserService(session)
        await user_service.update_user(telegram_user.id, privacy_consent=True)


@router.callback_query(F.data == "privacy_consent:0")
async def got_privacy_consent(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_caption(caption=callback.message.caption.replace("[ ]", "[❌]"))
    await callback.message.answer("Соглашение на обработку персональных данных <b>отклонено</b>, вы не можете "
                                  "пользоваться ботом, пересмотрите своё решение или обратитесь к администратору.",
                                  reply_markup=get_privacy_consent_rejected_keyboard())


@router.callback_query(F.data == "privacy_consent:retry")
async def got_privacy_consent_retry(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await require_privacy_consent(callback.message, state)
