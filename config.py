import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    RENDER_EXTERNAL_URL: str = os.getenv("RENDER_EXTERNAL_URL", "")
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS: str = "credentials.json"  # Файл с ключом
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    
    # Контакты
    MANAGER_USERNAME: str = "@IMIDZHRF"
    PHONE_NUMBER: str = "+7 967 341 1808"
    TELEGRAM_CHANNEL: str = "https://t.me/IMIDZH_RF"
    WEBSITE: str = "https://imidzh.ru"
    VK: str = "https://vk.com/imidzh_rf"
    INSTAGRAM: str = "https://instagram.com/imidzh_rf"
    
    # ID менеджера для уведомлений
    MANAGER_TELEGRAM_ID: int = int(os.getenv("MANAGER_TELEGRAM_ID", 0))

config = Config()
