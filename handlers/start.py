from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu
from database.sheets import db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Очищаем состояние
    await state.clear()
    
    # Сохраняем пользователя
    await db.save_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Приветственное сообщение
    welcome_text = (
        f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        "Мы — команда IMIDZH, помогаем малому и среднему бизнесу "
        "расти через качественный визуальный контент и digital-стратегию.\n\n"
        "📸 Что мы предлагаем:\n"
        "• Участие в розыгрыше бесплатной фотосъёмки\n"
        "• Бесплатную консультацию по продвижению\n"
        "• Профессиональный подход к вашему бренду\n\n"
        "Выберите нужный раздел в меню ниже 👇"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 <b>Помощь по боту</b>\n\n"
        "<b>Главное меню:</b>\n"
        "🎁 <b>Участие в розыгрыше</b> — регистрация на розыгрыш бесплатной фотосъёмки\n"
        "📞 <b>Связаться с нами</b> — контакты и способы связи\n"
        "💼 <b>Бесплатная консультация</b> — заявка на консультацию по продвижению\n\n"
        "<b>Команды:</b>\n"
        "/start — перезапустить бота\n"
        "/help — показать эту справку\n\n"
        "По любым вопросам: @IMIDZHRF"
    )
    await message.answer(help_text, parse_mode="HTML")

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Главное меню:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.message(F.text == "🔙 Назад в меню")
async def back_to_menu_text(message: Message, state: FSMContext):
    """Возврат в главное меню (текстовая кнопка)"""
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu()
    )