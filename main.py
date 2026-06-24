import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import config
from database.sheets import db
from handlers.start import router as start_router
from handlers.giveaway import router as giveaway_router
from handlers.contact import router as contact_router
from handlers.consultation import router as consultation_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(giveaway_router)
dp.include_router(contact_router)
dp.include_router(consultation_router)

async def set_commands():
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)

async def main():
    """Главная функция"""
    try:
        # Инициализация Google Sheets
        await db.initialize()
        logger.info("✅ Google Sheets подключен")
        
        # Установка команд
        await set_commands()
        
        # Запуск бота (polling)
        logger.info("✅ Бот запущен")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
