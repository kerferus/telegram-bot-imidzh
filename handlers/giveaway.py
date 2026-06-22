from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states.user_states import GiveawayStates
from keyboards.inline import get_consent_keyboard, get_phone_keyboard
from keyboards.main_menu import get_back_button
from database.sheets import db
from config import config

import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "🎁 Участие в розыгрыше")
async def start_giveaway(message: Message, state: FSMContext):
    """Начало ветки розыгрыша"""
    giveaway_text = (
        "🎁 <b>РОЗЫГРЫШ БЕСПЛАТНОЙ ФОТОСЪЁМКИ</b>\n\n"
        "Добро пожаловать!\n\n"
        "Мы запускаем розыгрыш бесплатной фотосъёмки "
        "для малого и среднего бизнеса.\n\n"
        "Если вы хотите, чтобы о вашем проекте узнали больше, "
        "а ваш бренд выглядел сильнее, заметнее и профессиональнее — "
        "это ваш шанс получить качественный визуальный контент для продвижения.\n\n"
        "📅 <b>Сроки проведения розыгрыша:</b>\n"
        "с 25 июня по 5 июля включительно.\n\n"
        "Чтобы принять участие, нажмите соответствующую кнопку "
        "и оставьте свои данные.\n\n"
        "Готовы развиваться вместе с нами и визуализировать "
        "свой проект для остальных? 🚀"
    )
    
    await message.answer(
        giveaway_text,
        parse_mode="HTML",
        reply_markup=get_consent_keyboard()
    )

@router.callback_query(F.data == "consent_yes")
async def consent_given(callback: CallbackQuery, state: FSMContext):
    """Пользователь дал согласие на обработку данных"""
    await state.set_state(GiveawayStates.waiting_for_last_name)
    
    await callback.message.delete()
    await callback.message.answer(
        "📝 <b>Анкета участника розыгрыша</b>\n\n"
        "Пожалуйста, ответьте на несколько вопросов.\n\n"
        "Введите вашу <b>фамилию</b>:",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )
    await callback.answer()

@router.message(GiveawayStates.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    """Обработка фамилии"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        from keyboards.main_menu import get_main_menu
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(last_name=message.text)
    await state.set_state(GiveawayStates.waiting_for_first_name)
    
    await message.answer(
        "Введите ваше <b>имя</b>:",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(GiveawayStates.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    """Обработка имени"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        from keyboards.main_menu import get_main_menu
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(first_name=message.text)
    await state.set_state(GiveawayStates.waiting_for_middle_name)
    
    await message.answer(
        "Введите ваше <b>отчество</b> (или напишите 'нет'):",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(GiveawayStates.waiting_for_middle_name)
async def process_middle_name(message: Message, state: FSMContext):
    """Обработка отчества"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        from keyboards.main_menu import get_main_menu
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    middle_name = message.text if message.text.lower() != 'нет' else ''
    await state.update_data(middle_name=middle_name)
    await state.set_state(GiveawayStates.waiting_for_phone)
    
    await message.answer(
        "📱 Укажите ваш <b>номер телефона</b>\n"
        "Или нажмите кнопку ниже, чтобы поделиться номером:",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )

@router.callback_query(F.data == "share_phone")
async def request_phone_contact(callback: CallbackQuery):
    """Запрос контакта через Telegram"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться номером", request_contact=True)],
            [KeyboardButton(text="🔙 Назад в меню")]
        ],
        resize_keyboard=True
    )
    
    await callback.message.delete()
    await callback.message.answer(
        "Нажмите кнопку ниже, чтобы поделиться номером телефона:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.message(GiveawayStates.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    """Обработка контакта телефона"""
    phone = message.contact.phone_number
    
    # Проверяем на дубликат
    if await db.check_phone_exists(phone):
        await message.answer(
            "❌ Данный номер телефона уже зарегистрирован в системе.\n"
            "Повторная регистрация невозможна.",
            reply_markup=get_back_button()
        )
        return
    
    await state.update_data(phone=phone)
    await state.set_state(GiveawayStates.waiting_for_organization)
    
    await message.answer(
        "🏢 Введите <b>название вашей организации</b>:",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(GiveawayStates.waiting_for_phone)
async def process_phone_text(message: Message, state: FSMContext):
    """Обработка телефона текстом"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        from keyboards.main_menu import get_main_menu
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    phone = message.text.strip()
    
    # Простая валидация телефона
    if len(phone) < 10:
        await message.answer(
            "❌ Пожалуйста, введите корректный номер телефона (минимум 10 цифр):",
            reply_markup=get_back_button()
        )
        return
    
    # Проверяем на дубликат
    if await db.check_phone_exists(phone):
        await message.answer(
            "❌ Данный номер телефона уже зарегистрирован в системе.\n"
            "Повторная регистрация невозможна.",
            reply_markup=get_back_button()
        )
        return
    
    await state.update_data(phone=phone)
    await state.set_state(GiveawayStates.waiting_for_organization)
    
    await message.answer(
        "🏢 Введите <b>название вашей организации</b>:",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(GiveawayStates.waiting_for_organization)
async def process_organization(message: Message, state: FSMContext):
    """Обработка названия организации"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        from keyboards.main_menu import get_main_menu
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(organization=message.text)
    await state.set_state(GiveawayStates.waiting_for_activity)
    
    await message.answer(
        "📋 Опишите <b>вид деятельности</b> вашей организации:\n"
        "<i>Например: производство мебели, ресторанный бизнес, IT-услуги и т.д.</i>",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(GiveawayStates.waiting_for_activity)
async def process_activity(message: Message, state: FSMContext):
    """Завершение анкеты розыгрыша"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        from keyboards.main_menu import get_main_menu
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    # Получаем все данные
    data = await state.get_data()
    data['activity_type'] = message.text
    data['telegram_id'] = message.from_user.id
    data['username'] = message.from_user.username
    data['consent_to_data_processing'] = True
    data['source'] = 'giveaway'
    
    # Сохраняем в Google Sheets
    success = await db.save_giveaway_participant(data)
    
    if success:
        # Отправляем уведомление менеджеру
        if config.MANAGER_TELEGRAM_ID:
            try:
                from main import bot
                manager_text = (
                    f"🔔 <b>Новая заявка на розыгрыш!</b>\n\n"
                    f"👤 {data['last_name']} {data['first_name']} {data.get('middle_name', '')}\n"
                    f"📱 {data['phone']}\n"
                    f"🏢 {data['organization']}\n"
                    f"📋 {data['activity_type']}\n"
                    f"📅 {data.get('registered_at', 'только что')}"
                )
                await bot.send_message(
                    config.MANAGER_TELEGRAM_ID,
                    manager_text,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления менеджеру: {e}")
        
        # Успешное завершение
        await message.answer(
            "✅ <b>Вы успешно зарегистрированы в розыгрыше!</b>\n\n"
            "Результаты будут объявлены после 5 июля.\n"
            "Желаем удачи! 🍀\n\n"
            "Следите за новостями в нашем канале: https://t.me/IMIDZH_RF",
            parse_mode="HTML",
            reply_markup=get_back_button()
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при сохранении данных.\n"
            "Пожалуйста, попробуйте позже или свяжитесь с менеджером: @IMIDZHRF",
            reply_markup=get_back_button()
        )
    
    await state.clear()