import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy import values

from database.database import SessionLocal
from database.models import Movie, Genre
from config import GOOGLE_SHEETS_ID, GOOGLE_CREDENTIALS_FILE, SHEET_NAME


def get_google_sheers_service():

    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE,scopes=scopes)
    service = build("sheers", "v4",credentials=creds)
    return service

def sync_movies():
    service = get_google_sheers_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=GOOGLE_SHEETS_ID,
        range=f"{SHEET_NAME}!A2:F"

    ).execute()

    values = result.get("values",[])


    if not values:
        print("Данные не найдены в таблице")
        return

    db = SessionLocal()

    try:
        for row in values:
            if len(row) <6:
                continue
            title, description, year, rating, genres_str, trailer_url = row
            # Проверяем существование фильма
            movie = db.query(Movie).filter(Movie.title == title).first()
            if not movie:
                movie = Movie(
                    title=title,
                    description=description,
                    year=int(year),
                    rating=float(rating),
                    trailer_url=trailer_url
                )
            # Обрабатываем жанр
            genres = []
            for genre_name in genres_str.split(","):
                genre_name = genre_name.split()
                genre = db.query(Genre).filter(Genre.name == genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    db.add(genre)
                genres.append(genre)


            movie.genres = genres

            db.add(movie)


        db.commit()
        print("Синхронизация успешно завершена!")
    except Exception as e:
        print(f"Ошибка при синхронизации: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_movies()
