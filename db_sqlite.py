import sqlite3  # Импортируем модуль для работы с SQLite базой данных

DB_FILE = "moviebot.db"  # Имя файла базы данных, в котором будут храниться данные

def get_conn():
    return sqlite3.connect(DB_FILE)  # Возвращает новое соединение с базой данных

def init_db():
    with get_conn() as conn:  # Открываем соединение с базой данных (автоматически закроется после блока with)
        cur = conn.cursor()  # Получаем курсор для выполнения SQL-запросов
        cur.execute("""      
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            query TEXT,                            
            success BOOLEAN,                       
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
        );
        """)
        conn.commit()

def save_search(query, success):
    with get_conn() as conn:  # Открываем соединение с базой данных
        cur = conn.cursor()   # Получаем курсор для выполнения SQL-запросов
        cur.execute("INSERT INTO search_history (query, success) VALUES (?, ?);", (query, success))
                               # Добавляем новую запись в таблицу search_history
        conn.commit()          # Подтверждаем изменения
