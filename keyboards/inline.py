from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_consent_keyboard():
    """Клавиатура согласия на обработку данных"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✅ Даю согласие на обработку персональных данных",
        callback_data="consent_yes"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад в меню",
        callback_data="back_to_menu"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_phone_keyboard():
    """Клавиатура для отправки номера телефона"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📱 Поделиться номером",
        callback_data="share_phone"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад в меню",
        callback_data="back_to_menu"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_contact_keyboard():
    """Клавиатура с контактами"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="👨‍💼 Написать менеджеру",
        url="https://t.me/IMIDZHRF"
    ))
    builder.add(InlineKeyboardButton(
        text="📞 Позвонить",
        callback_data="show_phone"
    ))
    builder.add(InlineKeyboardButton(
        text="📢 Наш Telegram-канал",
        url="https://t.me/IMIDZH_RF"
    ))
    builder.add(InlineKeyboardButton(
        text="🌐 Наш сайт",
        url="https://imidzh.ru"
    ))
    builder.add(InlineKeyboardButton(
        text="📱 ВКонтакте",
        url="https://vk.com/imidzh_rf"
    ))
    builder.add(InlineKeyboardButton(
        text="📸 Instagram",
        url="https://instagram.com/imidzh_rf"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад в меню",
        callback_data="back_to_menu"
    ))
    
    builder.adjust(1)
    return builder.as_markup()

def get_consultation_apply_keyboard():
    """Клавиатура для заявки на консультацию"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✍️ Оставить заявку",
        callback_data="apply_consultation"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад в меню",
        callback_data="back_to_menu"
    ))
    builder.adjust(1)
    return builder.as_markup()