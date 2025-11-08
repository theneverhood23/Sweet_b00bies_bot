# upgrade_db.py
import sqlite3

DB_NAME = 'stats.db'
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Получаем информацию о существующих колонках
cursor.execute("PRAGMA table_info(user_stats)")
columns = [info[1] for info in cursor.fetchall()]

# Список колонок, которые мы хотим добавить
new_columns = {
    'message_count_monthly': 'INTEGER DEFAULT 0', 'swear_count_monthly': 'INTEGER DEFAULT 0',
    'boobs_request_count_monthly': 'INTEGER DEFAULT 0', 'total_chars_count_monthly': 'INTEGER DEFAULT 0',
    'message_count_yearly': 'INTEGER DEFAULT 0', 'swear_count_yearly': 'INTEGER DEFAULT 0',
    'boobs_request_count_yearly': 'INTEGER DEFAULT 0', 'total_chars_count_yearly': 'INTEGER DEFAULT 0'
}

# Добавляем каждую новую колонку, если ее еще нет
for col_name, col_type in new_columns.items():
    if col_name not in columns:
        cursor.execute(f"ALTER TABLE user_stats ADD COLUMN {col_name} {col_type}")
        print(f"Добавлена колонка: {col_name}")

conn.commit()
conn.close()
print("Миграция базы данных завершена.")
