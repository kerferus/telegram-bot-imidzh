from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.inline import get_contact_keyboard
from config import config

router = Router()

@router.message(F.text == "📞 Связаться с нами")
async def show_contacts(message: Message):
    """Показать контакты"""
    contact_text = (
        "📞 <b>Свяжитесь с нами удобным способом:</b>\n\n"
        "Выберите один из вариантов ниже 👇"
    )
    
    await message.answer(
        contact_text,
        parse_mode="HTML",
        reply_markup=get_contact_keyboard()
    )

@router.callback_query(F.data == "show_phone")
async def show_phone_number(callback: CallbackQuery):
    """Показать номер телефона"""
    phone_text = (
        f"📞 <b>Наш телефон:</b>\n"
        f"<code>{config.PHONE_NUMBER}</code>\n\n"
        f"Звоните, будем рады помочь!"
    )
    
    await callback.message.answer(phone_text, parse_mode="HTML")
    await callback.answer()