import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

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

# Инициализация бота
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Webhook настройки
WEBHOOK_PATH = f"/webhook/{config.BOT_TOKEN}"
WEBHOOK_URL = f"{config.RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(giveaway_router)
dp.include_router(contact_router)
dp.include_router(consultation_router)

# Health check endpoint
async def health_check(request):
    return web.Response(text="Bot is running!")

# Настройка приложения
async def on_startup(bot: Bot):
    try:
        await db.initialize()
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
        logger.info(f"✅ Бот запущен. Webhook: {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        raise

async def on_shutdown(bot: Bot):
    try:
        await bot.delete_webhook()
        await bot.session.close()
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка при остановке: {e}")

def main():
    app = web.Application()
    
    app.router.add_get("/", health_check)
    
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))
    
    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()
