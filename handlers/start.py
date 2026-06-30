from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from keyboards.main_menu import get_main_menu
from database.sheets import db

router = Router()

# ID канала (если не работает, узнай числовой ID через @userinfobot)
CHANNEL_ID = "@IMIDZH_RF"
CHANNEL_URL = "https://t.me/IMIDZH_RF"

async def check_subscription(bot, user_id: int) -> bool:
    """Проверка подписки на канал"""
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return chat_member.status not in ['left', 'kicked', 'banned']
    except Exception:
        return False

def get_channel_keyboard():
    """Клавиатура для проверки подписки"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📢 Подписаться на канал",
        url=CHANNEL_URL
    ))
    builder.add(InlineKeyboardButton(
        text="✅ Я подписался",
        callback_data="check_subscription"
    ))
    builder.adjust(1)
    return builder.as_markup()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    # Сохраняем пользователя
    await db.save_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Проверяем подписку
    is_subscribed = await check_subscription(message.bot, message.from_user.id)
    
    # Приветственный текст
    welcome_text = (
        f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        "Мы — команда IMIDZH, помогаем малому и среднему бизнесу "
        "расти через качественный визуальный контент и digital-стратегию."
    )
    
    menu_text = (
        f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        "Мы — команда IMIDZH, помогаем малому и среднему бизнесу "
        "расти через качественный визуальный контент и digital-стратегию.\n\n"
        "📸 Что мы предлагаем:\n"
        "• Участие в розыгрыше бесплатной фотосъёмки\n"
        "• Бесплатную консультацию по продвижению\n"
        "• Профессиональный подход к вашему бренду\n\n"
        "Выберите нужный раздел в меню ниже 👇"
    )
    
    try:
        # Пытаемся отправить фото
        photo = FSInputFile("welcome.jpg")
        
        if not is_subscribed:
            await message.answer_photo(
                photo=photo,
                caption=welcome_text + "\n\n⚠️ <b>Для использования бота необходимо подписаться на наш канал!</b>\n\nПодпишитесь и нажмите кнопку проверки 👇",
                parse_mode="HTML",
                reply_markup=get_channel_keyboard()
            )
        else:
            await message.answer_photo(
                photo=photo,
                caption=menu_text,
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )
    except Exception:
        # Если фото нет - отправляем без фото
        if not is_subscribed:
            await message.answer(
                welcome_text + "\n\n⚠️ <b>Для использования бота необходимо подписаться на наш канал!</b>\n\nПодпишитесь и нажмите кнопку проверки 👇",
                parse_mode="HTML",
                reply_markup=get_channel_keyboard()
            )
        else:
            await message.answer(
                menu_text,
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )

@router.callback_query(F.data == "check_subscription")
async def check_sub(callback: CallbackQuery, state: FSMContext):
    """Проверка подписки после нажатия кнопки"""
    is_subscribed = await check_subscription(callback.bot, callback.from_user.id)
    
    if is_subscribed:
        await callback.message.delete()
        
        menu_text = (
            f"👋 Добро пожаловать, {callback.from_user.first_name}!\n\n"
            "Спасибо за подписку! 🎉\n\n"
            "📸 Что мы предлагаем:\n"
            "• Участие в розыгрыше бесплатной фотосъёмки\n"
            "• Бесплатную консультацию по продвижению\n"
            "• Профессиональный подход к вашему бренду\n\n"
            "Выберите нужный раздел в меню ниже 👇"
        )
        
        try:
            photo = FSInputFile("welcome.jpg")
            await callback.message.answer_photo(
                photo=photo,
                caption=menu_text,
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )
        except Exception:
            await callback.message.answer(
                menu_text,
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )
        
        await callback.answer("✅ Подписка подтверждена!")
    else:
        await callback.answer("❌ Вы ещё не подписались на канал!", show_alert=True)

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
