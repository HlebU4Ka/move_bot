from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from database.database import SessionLocal
from database.models.models import Movie, Genre
from config import GOOGLE_SHEETS_ID, GOOGLE_CREDENTIALS_FILE, SHEET_NAME


def get_google_sheets_service():
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)
    return service


def get_sheet_properties(service):
    try:
        # Получаем информацию о таблице
        spreadsheet = service.spreadsheets().get(spreadsheetId=GOOGLE_SHEETS_ID).execute()
        sheets = spreadsheet.get('sheets', [])

        # Выводим доступные листы
        print("Доступные листы:")
        for sheet in sheets:
            print(f"- {sheet['properties']['title']}")

        return sheets
    except Exception as e:
        print(f"Ошибка при получении информации о таблице: {e}")
        return None


def sync_movies():
    try:
        service = get_google_sheets_service()

        # Получаем информацию о листах
        sheets = get_sheet_properties(service)
        if not sheets:
            print("Не удалось получить информацию о листах таблицы")
            return

        # Проверяем существование нужного листа
        sheet_exists = False
        for sheet in sheets:
            if sheet['properties']['title'] == SHEET_NAME:
                sheet_exists = True
                break

        if not sheet_exists:
            print(f"Лист '{SHEET_NAME}' не найден в таблице")
            return

        # Получаем данные из Google Sheets
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=GOOGLE_SHEETS_ID,
                range=f"'{SHEET_NAME}'!A2:F"  # Заключаем название листа в кавычки
            ).execute()
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return

        values = result.get('values', [])

        if not values:
            print('Данные не найдены в таблице')
            return

        print(f"Найдено {len(values)} строк данных")

        db = SessionLocal()

        try:
            for i, row in enumerate(values, start=2):  # start=2 потому что начинаем с A2
                try:
                    if len(row) < 6:
                        print(f"Пропущена строка {i}: недостаточно данных")
                        continue

                    title, description, year, rating, genres_str, trailer_url = row

                    # Проверяем и конвертируем данные
                    try:
                        year = int(year)
                        rating = float(rating)
                    except ValueError as e:
                        print(f"Ошибка в строке {i}: неверный формат года или рейтинга")
                        continue

                    # Проверяем существование фильма
                    movie = db.query(Movie).filter(Movie.title == title).first()
                    if not movie:
                        movie = Movie(
                            title=title,
                            description=description,
                            year=year,
                            rating=rating,
                            trailer_url=trailer_url
                        )
                        print(f"Добавлен новый фильм: {title}")

                    # Обрабатываем жанры
                    genres = []
                    for genre_name in genres_str.split(','):
                        genre_name = genre_name.strip()
                        if genre_name:  # Проверяем, что жанр не пустой
                            genre = db.query(Genre).filter(Genre.name == genre_name).first()
                            if not genre:
                                genre = Genre(name=genre_name)
                                db.add(genre)
                                print(f"Добавлен новый жанр: {genre_name}")
                            genres.append(genre)

                    movie.genres = genres
                    db.add(movie)

                except Exception as row_error:
                    print(f"Ошибка при обработке строки {i}: {row_error}")
                    continue

            db.commit()
            print("Синхронизация успешно завершена!")

        except Exception as e:
            print(f"Ошибка при синхронизации с базой данных: {e}")
            db.rollback()
        finally:
            db.close()

    except Exception as e:
        print(f"Ошибка при подключении к Google Sheets: {e}")


if __name__ == "__main__":
    print("Начало синхронизации...")
    print(f"ID таблицы: {GOOGLE_SHEETS_ID}")
    print(f"Имя листа: {SHEET_NAME}")
    sync_movies() 