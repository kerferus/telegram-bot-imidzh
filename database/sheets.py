import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import List, Dict, Optional
import logging
import json
import os

from config import config

logger = logging.getLogger(__name__)

class GoogleSheetsDB:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self.spreadsheet = None
        
        # Инициализация листов
        self.giveaway_sheet = None  # Участники розыгрыша
        self.consultation_sheet = None  # Заявки на консультации
        self.users_sheet = None  # Пользователи
    
    async def initialize(self):
        """Инициализация подключения к Google Sheets"""
        try:
            # Если credentials в env переменной (для Render)
            if os.getenv("GOOGLE_CREDS_JSON"):
                creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds_dict, self.scope
                )
            else:
                # Локальный файл
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    config.GOOGLE_SHEETS_CREDENTIALS, self.scope
                )
            
            self.client = gspread.authorize(credentials)
            
            # Открываем таблицу
            if config.SPREADSHEET_ID:
                self.spreadsheet = self.client.open_by_key(config.SPREADSHEET_ID)
            else:
                # Создаем новую таблицу
                self.spreadsheet = self.client.create('Telegram Bot - Заявки')
                # Делаем её публичной (опционально)
                # self.spreadsheet.share(None, perm_type='anyone', role='reader')
                logger.info(f"Создана новая таблица с ID: {self.spreadsheet.id}")
            
            # Инициализируем листы
            await self._init_sheets()
            
            logger.info("✅ Google Sheets подключен")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Google Sheets: {e}")
            raise
    
    async def _init_sheets(self):
        """Инициализация листов с заголовками"""
        # Лист для розыгрыша
        try:
            self.giveaway_sheet = self.spreadsheet.worksheet("Розыгрыш")
        except:
            self.giveaway_sheet = self.spreadsheet.add_worksheet(
                title="Розыгрыш", rows=1000, cols=20
            )
            # Добавляем заголовки
            self.giveaway_sheet.append_row([
                "ID", "Дата регистрации", "Telegram ID", "Username",
                "Фамилия", "Имя", "Отчество", "Телефон",
                "Название организации", "Вид деятельности",
                "Согласие на обработку", "Источник"
            ])
        
        # Лист для консультаций
        try:
            self.consultation_sheet = self.spreadsheet.worksheet("Консультации")
        except:
            self.consultation_sheet = self.spreadsheet.add_worksheet(
                title="Консультации", rows=1000, cols=20
            )
            self.consultation_sheet.append_row([
                "ID", "Дата создания", "Telegram ID", "Username",
                "Имя", "Телефон", "Компания", "Описание запроса",
                "Источник"
            ])
        
        # Лист для пользователей
        try:
            self.users_sheet = self.spreadsheet.worksheet("Пользователи")
        except:
            self.users_sheet = self.spreadsheet.add_worksheet(
                title="Пользователи", rows=1000, cols=20
            )
            self.users_sheet.append_row([
                "ID", "Telegram ID", "Username", "First Name",
                "Last Name", "Дата регистрации", "Последняя активность"
            ])
    
    async def save_user(self, telegram_id: int, username: str, 
                        first_name: str, last_name: str):
        """Сохранение пользователя"""
        try:
            # Проверяем, существует ли пользователь
            all_users = self.users_sheet.get_all_values()
            for i, row in enumerate(all_users[1:], start=2):  # Пропускаем заголовок
                if len(row) > 1 and row[1] == str(telegram_id):
                    # Обновляем существующего
                    self.users_sheet.update(f'C{i}:G{i}', [[
                        username, first_name, last_name,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]])
                    return
            
            # Добавляем нового
            self.users_sheet.append_row([
                len(all_users),  # ID
                telegram_id,
                username,
                first_name,
                last_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
        except Exception as e:
            logger.error(f"Ошибка сохранения пользователя: {e}")
    
    async def check_phone_exists(self, phone: str) -> bool:
        """Проверка существования телефона"""
        try:
            # Проверяем в розыгрыше
            giveaway_data = self.giveaway_sheet.get_all_values()
            for row in giveaway_data[1:]:
                if len(row) > 7 and row[7] == phone:
                    return True
            
            # Проверяем в консультациях
            consultation_data = self.consultation_sheet.get_all_values()
            for row in consultation_data[1:]:
                if len(row) > 5 and row[5] == phone:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки телефона: {e}")
            return False
    
    async def save_giveaway_participant(self, data: dict) -> bool:
        """Сохранение участника розыгрыша"""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_rows = self.giveaway_sheet.get_all_values()
            row_id = len(all_rows)
            
            self.giveaway_sheet.append_row([
                row_id,  # ID
                now,  # Дата регистрации
                data.get('telegram_id'),
                data.get('username'),
                data.get('last_name'),  # Фамилия
                data.get('first_name'),  # Имя
                data.get('middle_name', ''),  # Отчество
                data.get('phone'),  # Телефон
                data.get('organization'),  # Организация
                data.get('activity_type'),  # Вид деятельности
                "Да" if data.get('consent_to_data_processing') else "Нет",
                data.get('source', 'giveaway')
            ])
            
            logger.info(f"✅ Участник розыгрыша сохранен: {data.get('last_name')} {data.get('first_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения участника розыгрыша: {e}")
            return False
    
    async def save_consultation_request(self, data: dict) -> bool:
        """Сохранение заявки на консультацию"""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_rows = self.consultation_sheet.get_all_values()
            row_id = len(all_rows)
            
            self.consultation_sheet.append_row([
                row_id,  # ID
                now,  # Дата создания
                data.get('telegram_id'),
                data.get('username'),
                data.get('name'),  # Имя
                data.get('phone'),  # Телефон
                data.get('company'),  # Компания
                data.get('request_description', ''),  # Описание запроса
                data.get('source', 'consultation')
            ])
            
            logger.info(f"✅ Заявка на консультацию сохранена: {data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения заявки: {e}")
            return False
    
    async def get_stats(self) -> dict:
        """Получение статистики"""
        try:
            giveaway_count = len(self.giveaway_sheet.get_all_values()) - 1  # Минус заголовок
            consultation_count = len(self.consultation_sheet.get_all_values()) - 1
            users_count = len(self.users_sheet.get_all_values()) - 1
            
            return {
                "giveaway": max(0, giveaway_count),
                "consultation": max(0, consultation_count),
                "users": max(0, users_count)
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"giveaway": 0, "consultation": 0, "users": 0}

# Глобальный экземпляр
db = GoogleSheetsDB()