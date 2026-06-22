from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu():
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🎁 Участие в розыгрыше"))
    builder.add(KeyboardButton(text="📞 Связаться с нами"))
    builder.add(KeyboardButton(text="💼 Бесплатная консультация"))
    
    builder.adjust(1)  # По одной кнопке в ряд
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел..."
    )

def get_back_button():
    """Кнопка Назад"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Назад в меню"))
    return builder.as_markup(resize_keyboard=True)