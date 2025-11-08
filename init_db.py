# init_db.py
import sqlite3

DB_NAME = 'stats.db'

# Подключаемся к базе (она создастся, если ее нет)
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Создаем таблицу для статистики пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        message_count INTEGER DEFAULT 0,
        swear_count INTEGER DEFAULT 0,
        boobs_request_count INTEGER DEFAULT 0,
        total_chars_count INTEGER DEFAULT 0
    )
''')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print(f"База данных '{DB_NAME}' успешно создана/проверена.")
