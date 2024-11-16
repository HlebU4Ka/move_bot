from msilib import init_database

from database.database import  engine
from database.models.models import Base

def init_database():
    Base.metadate.create_all(bind=engine)

    if __name__ == "__main__":
        print("Инициализация базы данных...")
        init_database()
        print("База данных успешно инициализирована!")
