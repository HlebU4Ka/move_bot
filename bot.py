import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database.database import SessionLocal
from database.models.models import Movie, Genre, WatchedMovies
from config import TELEGRAM_TOKEN
import random
from datetime import datetime
#
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        'Привет! Я бот для рекомендации фильмов. '
        'Используйте следующие команды:\n'
        '/random - получить случайный фильм\n'
        '/genres - показать список жанров\n'
        '/watched - показать просмотренные фильмы'
    )


async def random_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет случайный фильм"""
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        if not movies:
            await update.message.reply_text('В базе данных нет фильмов')
            return

        movie = random.choice(movies)
        await send_movie_info(update, movie)
    finally:
        db.close()


async def genres(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает список доступных жанров"""
    db = SessionLocal()
    try:
        genres = db.query(Genre).all()
        keyboard = []
        for genre in genres:
            keyboard.append([InlineKeyboardButton(genre.name, callback_data=f'genre_{genre.id}')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Выберите жанр:', reply_markup=reply_markup)
    finally:
        db.close()


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith('genre_'):
        genre_id = int(query.data.split('_')[1])
        db = SessionLocal()
        try:
            genre = db.query(Genre).filter(Genre.id == genre_id).first()
            if genre and genre.movies:
                movie = random.choice(genre.movies)
                await send_movie_info(update, movie, query=query)
            else:
                await query.edit_message_text('Фильмы данного жанра не найдены')
        finally:
            db.close()
    elif query.data.startswith('watch_'):
        await mark_watched(update, context)


async def send_movie_info(update: Update, movie: Movie, query=None) -> None:
    """Отправляет информацию о фильме"""
    genres_str = ', '.join([genre.name for genre in movie.genres])
    message = (
        f'🎬 *{movie.title}*\n\n'
        f'📝 {movie.description}\n\n'
        f'📅 Год: {movie.year}\n'
        f'⭐️ Рейтинг: {movie.rating}\n'
        f'🎭 Жанры: {genres_str}\n'
        f'🎦 [Трейлер]({movie.trailer_url})'
    )

    keyboard = [[InlineKeyboardButton("Отметить как просмотренный", callback_data=f'watch_{movie.id}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text=message, reply_markup=reply_markup, parse_mode='Markdown')


async def mark_watched(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отмечает фильм как просмотренный"""
    query = update.callback_query
    movie_id = int(query.data.split('_')[1])
    user_id = update.effective_user.id

    db = SessionLocal()
    try:
        watched = WatchedMovies(
            user_id=user_id,
            movie_id=movie_id,
            watched_date=datetime.utcnow()
        )
        db.add(watched)
        db.commit()
        await query.answer('Фильм отмечен как просмотренный!')
    except Exception as e:
        logger.error(f"Error marking movie as watched: {e}")
        await query.answer('Произошла ошибка')
    finally:
        db.close()


async def watched_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает список просмотренных фильмов"""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        watched_movies = db.query(WatchedMovies).filter(WatchedMovies.user_id == user_id).all()
        if not watched_movies:
            await update.message.reply_text('Вы еще не отметили ни одного просмотренного фильма')
            return

        message = "Просмотренные фильмы:\n\n"
        for watched in watched_movies:
            movie = watched.movie
            message += f"🎬 {movie.title} ({movie.year})\n"

        await update.message.reply_text(message)
    finally:
        db.close()


async def shutdown(application: Application) -> None:
    """Корректное завершение работы бота"""
    try:
        if application.is_initialized():
            await application.stop()
            await application.shutdown()
    except Exception as e:
        logger.error(f"Ошибка при завершении работы бота: {e}")
#
#
# # async def main() -> None:
# #     """Запуск бота"""
# #     application = None
# #     try:
# #         application = Application.builder().token(TELEGRAM_TOKEN).build()
# #
# #         # Добавляем обработчики команд
# #         application.add_handler(CommandHandler("start", start))
# #         application.add_handler(CommandHandler("random", random_movie))
# #         application.add_handler(CommandHandler("genres", genres))
# #         application.add_handler(CommandHandler("watched", watched_list))
# #         application.add_handler(CallbackQueryHandler(button))
# #
# #         # Запускаем бота
# #         await application.initialize()
# #         await application.start()
# #         await application.run_polling()
# #
# #     except Exception as e:
# #         logger.error(f"Ошибка при запуске бота: {e}")
# #     finally:
# #         if application:
# #             await shutdown(application)
# #
# #
# # if __name__ == '__main__':
# #     try:
# #         asyncio.run(main())
# #     except KeyboardInterrupt:
# #         logger.info("Бот остановлен пользователем")
# #     except Exception as e:
# #         logger.error(f"Критическая ошибка: {e}")
#


import logging.handlers
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database.database import SessionLocal
from database.models.models import Movie, Genre, WatchedMovies
from config import TELEGRAM_TOKEN
import random
from datetime import datetime


# Настройка логирования
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Хендлер для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Хендлер для вывода в файл
    file_handler = logging.handlers.RotatingFileHandler(
        'bot.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Инициализация логгера
logger = setup_logging()


# [Все остальные функции обработчиков остаются без изменений]

async def main() -> None:
    """Запуск бота"""
    # Инициализация приложения
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_movie))
    app.add_handler(CommandHandler("genres", genres))
    app.add_handler(CommandHandler("watched", watched_list))
    app.add_handler(CallbackQueryHandler(button))

    # Запускаем бота
    logger.info("Запуск бота...")

    # Запускаем бота и ждем его завершения
    await app.initialize()
    await app.start()
    await app.run_polling(allowed_updates=Update.ALL_TYPES)
    await app.stop()


if __name__ == '__main__':
    try:
        # Запускаем бота в асинхронном режиме
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        # Убеждаемся, что все асинхронные задачи завершены
        pending = asyncio.all_tasks()
        for task in pending:
            task.cancel()