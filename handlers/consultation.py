from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.user_states import ConsultationStates
from keyboards.inline import get_consultation_apply_keyboard, get_phone_keyboard
from keyboards.main_menu import get_back_button, get_main_menu
from database.sheets import db
from config import config

import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "💼 Бесплатная консультация")
async def start_consultation(message: Message):
    """Начало ветки консультации"""
    consultation_text = (
        "💼 <b>БЕСПЛАТНАЯ КОНСУЛЬТАЦИЯ</b>\n\n"
        "Помогаем бизнесу уже 1 год выстроить продвижение:\n"
        "📱 соцсети\n"
        "📢 каналы\n"
        "📊 реклама\n"
        "🎯 лиды\n"
        "🎨 визуальный стиль\n"
        "💻 digital-стратегия\n\n"
        "Оставьте заявку, и мы поможем вашему бизнесу расти!"
    )
    
    await message.answer(
        consultation_text,
        parse_mode="HTML",
        reply_markup=get_consultation_apply_keyboard()
    )

@router.callback_query(F.data == "apply_consultation")
async def apply_consultation(callback: CallbackQuery, state: FSMContext):
    """Начало заполнения заявки на консультацию"""
    await state.set_state(ConsultationStates.waiting_for_name)
    
    await callback.message.delete()
    await callback.message.answer(
        "📝 <b>Заявка на консультацию</b>\n\n"
        "Введите ваше <b>имя</b>:",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )
    await callback.answer()

@router.message(ConsultationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(name=message.text)
    await state.set_state(ConsultationStates.waiting_for_phone)
    
    await message.answer(
        "📱 Укажите ваш <b>номер телефона</b>:",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )

@router.callback_query(F.data == "share_phone")
async def request_phone_contact_consultation(callback: CallbackQuery):
    """Запрос контакта для консультации"""
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

@router.message(ConsultationStates.waiting_for_phone, F.contact)
async def process_phone_contact_consultation(message: Message, state: FSMContext):
    """Обработка контакта телефона"""
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await state.set_state(ConsultationStates.waiting_for_company)
    
    await message.answer(
        "🏢 Введите <b>название компании</b>:",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(ConsultationStates.waiting_for_phone)
async def process_phone_text_consultation(message: Message, state: FSMContext):
    """Обработка телефона текстом"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(phone=message.text.strip())
    await state.set_state(ConsultationStates.waiting_for_company)
    
    await message.answer(
        "🏢 Введите <b>название компании</b>:",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(ConsultationStates.waiting_for_company)
async def process_company(message: Message, state: FSMContext):
    """Обработка названия компании"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(company=message.text)
    await state.set_state(ConsultationStates.waiting_for_description)
    
    await message.answer(
        "💬 Кратко опишите ваш <b>запрос</b>:\n"
        "<i>Что вас интересует, какие задачи стоят перед бизнесом?</i>",
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.message(ConsultationStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Завершение заявки на консультацию"""
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    # Получаем все данные
    data = await state.get_data()
    data['request_description'] = message.text
    data['telegram_id'] = message.from_user.id
    data['username'] = message.from_user.username
    data['source'] = 'consultation'
    
    # Сохраняем в Google Sheets
    success = await db.save_consultation_request(data)
    
    if success:
        # Уведомление менеджеру
        if config.MANAGER_TELEGRAM_ID:
            try:
                from main import bot
                manager_text = (
                    f"🔔 <b>Новая заявка на консультацию!</b>\n\n"
                    f"👤 {data['name']}\n"
                    f"📱 {data['phone']}\n"
                    f"🏢 {data['company']}\n"
                    f"💬 {data['request_description']}\n"
                    f"📅 {data.get('created_at', 'только что')}"
                )
                await bot.send_message(
                    config.MANAGER_TELEGRAM_ID,
                    manager_text,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления: {e}")
        
        await message.answer(
            "✅ <b>Спасибо, заявка на консультацию принята!</b>\n\n"
            "Мы свяжемся с вами в ближайшее время.\n\n"
            "А пока можете подписаться на наш канал: https://t.me/IMIDZH_RF",
            parse_mode="HTML",
            reply_markup=get_back_button()
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при сохранении заявки.\n"
            "Пожалуйста, свяжитесь с нами напрямую: @IMIDZHRF",
            reply_markup=get_back_button()
        )
    
    await state.clear()