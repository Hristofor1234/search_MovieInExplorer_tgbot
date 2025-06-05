import sqlite3  # Импортируем модуль для работы с SQLite базой данных

DB_FILE = "moviebot.db"  # Имя файла базы данных, в котором будут храниться данные

def get_conn():
    return sqlite3.connect(DB_FILE)  # Возвращает новое соединение с базой данных

def init_db():
    with get_conn() as conn:  # Открываем соединение с базой данных (автоматически закроется после блока with)
        cur = conn.cursor()  # Получаем курсор для выполнения SQL-запросов
        cur.execute("""      # Выполняем SQL-запрос на создание таблицы, если она ещё не существует
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID запроса (автоматически увеличивается)
            query TEXT,                            -- Название фильма, которое искал пользователь
            success BOOLEAN,                       -- Был ли запрос успешным (True/False)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  -- Дата и время запроса по умолчанию — текущее
        );
        """)
        conn.commit()  # Сохраняем изменения в базе данных

def save_search(query, success):
    with get_conn() as conn:  # Открываем соединение с базой данных
        cur = conn.cursor()   # Получаем курсор для выполнения SQL-запросов
        cur.execute("INSERT INTO search_history (query, success) VALUES (?, ?);", (query, success))
                               # Добавляем новую запись в таблицу search_history
        conn.commit()          # Подтверждаем изменения
