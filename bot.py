import logging                           # Модуль для логирования информации (ошибки, события)
import os                                # Модуль для работы с переменными окружения и путями
import requests                          # Модуль для HTTP-запросов (используется для доступа к OMDb API)
from telegram import Update              # Объект, представляющий входящее сообщение от Telegram
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
                                         # Компоненты Telegram бота: построение приложения, обработка сообщений и команд, фильтры и контекст
from dotenv import load_dotenv           # Загрузка переменных окружения из файла .env
from db_sqlite import init_db, save_search
                                         # Инициализация базы данных и сохранение истории поиска
from deep_translator import GoogleTranslator
                                         # Импорт переводчика Google (через библиотеку deep_translator)

# === Настройка ===
load_dotenv()                            # Загрузка значений из .env в переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")       # Токен Telegram-бота из переменной окружения
OMDB_API_KEY = os.getenv("OMDB_API_KEY") # Ключ API от OMDb (для поиска фильмов)
translator = GoogleTranslator(source='auto', target='en')     # Переводчик для перевода пользовательского ввода на английский
translator_ru = GoogleTranslator(source='en', target='ru')    # Переводчик для перевода названий/сюжетов обратно на русский

logging.basicConfig(level=logging.INFO)  # Настройка уровня логирования
logger = logging.getLogger(__name__)     # Создание логгера

init_db()                                # Инициализация базы данных (если таблицы не созданы — создать)

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи название фильма, и я найду о нём информацию.")
                                         # Обработка команды /start — отправка приветственного сообщения

# === Поиск фильма ===
async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()  # Получаем текст сообщения пользователя и убираем пробелы
    if not query:
        await update.message.reply_text("Введите название фильма.")  # Сообщение, если пользователь ничего не ввёл
        return

    try:
        # Перевод названия на английский
        translated_query = translator.translate(query)  # Перевод пользовательского ввода на английский
        logger.info(f"Переведённый запрос: {translated_query}")  # Логируем перевод

        url = f"http://www.omdbapi.com/?t={translated_query}&apikey={OMDB_API_KEY}&plot=full&r=json"
                                         # Формируем URL для запроса к OMDb API

        response = requests.get(url).json()  # Отправляем GET-запрос и парсим ответ как JSON
        logger.info(f"Ответ OMDb: {response}")  # Логируем полученный ответ

        if response.get("Response") == "True":  # Проверяем, найден ли фильм
            title = response.get("Title")      # Получаем оригинальное название фильма
            year = response.get("Year")        # Год выпуска
            director = response.get("Director")# Режиссёр
            genre = response.get("Genre")      # Жанр
            plot = response.get("Plot")        # Сюжет
            imdb = response.get("imdbRating")  # Рейтинг IMDb

            # Переводим название и сюжет обратно на русский
            title_ru = translator_ru.translate(title)  # Переводим название
            plot_ru = translator_ru.translate(plot)    # Переводим сюжет

            message = (                             # Формируем сообщение с информацией о фильме
                f"🎬 <b>{title_ru}</b> ({year})\n"
                f"🎞 Жанр: {genre}\n"
                f"🎬 Режиссёр: {director}\n"
                f"⭐ IMDb: {imdb}\n"
                f"📝 Сюжет: {plot_ru}"
            )
            save_search(query, True)                # Сохраняем удачный запрос в БД
            await update.message.reply_text(message, parse_mode="HTML")  # Отправляем сообщение пользователю
        else:
            save_search(query, False)               # Сохраняем неудачный запрос в БД
            await update.message.reply_text("Фильм не найден.")  # Сообщение, если фильм не найден
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")      # Логируем исключение
        await update.message.reply_text("Произошла ошибка при поиске фильма.")  # Сообщение об ошибке пользователю

# === Запуск ===
if __name__ == "__main__":
    if not BOT_TOKEN or not OMDB_API_KEY:
        raise ValueError("BOT_TOKEN или OMDB_API_KEY не указан в .env")  # Проверка на наличие ключей

    app = Application.builder().token(BOT_TOKEN).build()  # Создаём Telegram-приложение

    app.add_handler(CommandHandler("start", start))  # Регистрируем обработчик команды /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))  # Обрабатываем все текстовые сообщения

    print("Бот запущен...")  # Сообщение в консоль
    app.run_polling()        # Запускаем бот в режиме long polling
