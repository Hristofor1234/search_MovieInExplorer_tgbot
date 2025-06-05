import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv
from db_sqlite import init_db, save_search
from deep_translator import GoogleTranslator

# === Настройка ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
translator = GoogleTranslator(source='auto', target='en')
translator_ru = GoogleTranslator(source='en', target='ru')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init_db()

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи название фильма, и я найду о нём информацию.")

# === Поиск фильма ===
async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query:
        await update.message.reply_text("Введите название фильма.")
        return

    try:
        # Перевод названия на английский
        translated_query = translator.translate(query)
        logger.info(f"Переведённый запрос: {translated_query}")

        url = f"http://www.omdbapi.com/?t={translated_query}&apikey={OMDB_API_KEY}&plot=full&r=json"
        response = requests.get(url).json()
        logger.info(f"Ответ OMDb: {response}")

        if response.get("Response") == "True":
            title = response.get("Title")
            year = response.get("Year")
            director = response.get("Director")
            genre = response.get("Genre")
            plot = response.get("Plot")
            imdb = response.get("imdbRating")

            # Переводим название и сюжет обратно на русский
            title_ru = translator_ru.translate(title)
            plot_ru = translator_ru.translate(plot)

            message = (
                f"🎬 <b>{title_ru}</b> ({year})\n"
                f"🎞 Жанр: {genre}\n"
                f"🎬 Режиссёр: {director}\n"
                f"⭐ IMDb: {imdb}\n"
                f"📝 Сюжет: {plot_ru}"
            )
            save_search(query, True)
            await update.message.reply_text(message, parse_mode="HTML")
        else:
            save_search(query, False)
            await update.message.reply_text("Фильм не найден.")
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        await update.message.reply_text("Произошла ошибка при поиске фильма.")

# === Запуск ===
if __name__ == "__main__":
    if not BOT_TOKEN or not OMDB_API_KEY:
        raise ValueError("BOT_TOKEN или OMDB_API_KEY не указан в .env")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

    print("Бот запущен...")
    app.run_polling()
