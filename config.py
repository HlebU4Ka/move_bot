import os
from dotenv import load_dotenv

load_dotenv()

"""
Конфигурации получения ключей\подключения к боту.
"""

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Не указан TELEGRAM_TOKEN в .env файле.")

DATABASE_URL = os.getenv("DATABASE_URL")
if not TELEGRAM_TOKEN:
    raise ValueError("Не указан DATABASE_URL в .env файле.")

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")


if not GOOGLE_SHEETS_ID:
    raise ValueError("Не указан GOOGLE_SHEETS_ID в .env файле.")
if not GOOGLE_CREDENTIALS_FILE:
    raise ValueError("Не указан GOOGLE_CREDENTIALS_FILE в .env файле.")

SHEET_NAME = "Movies"
UPDATE_INTERVAL = 24*60*60