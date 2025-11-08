import datetime
import pytz
import os
import logging
import requests
import re
import random
import sqlite3
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование, чтобы видеть ошибки в терминале
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из файла .env (в нашем случае TELEGRAM_TOKEN)
# Попробуем загрузить стандартный .env; если токен не найден, попробуем специфичный файл
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Константы для новой фичи
DB_NAME = 'stats.db'
SWEAR_WORDS = ['блять', 'пиздец', 'ебать', 'хуй', 'пидор'] # Дополни список по вкусу
ADMIN_IDS = ['Theneverhood23'] # <-- ВАЖНО: Впиши сюда свой Telegram User ID
CHAT_ID_FOR_STATS = -1002916490314
TIMEZONE = pytz.timezone('Europe/Moscow')

# Триггер-фразы, на которые хуй в польто будет реагировать бот (приводим к нижнему регистру)
TRIGGER_PHRASE_BOOBS = "скинь сиськи"
## ДОБАВЛЕНО: Новая триггер-фраза
TRIGGER_PHRASE_DICK = "скинь член"
TRIGGER_PHRASE_BASH = "скинь ржаку"
TRIGGER_PHRASE_BANYA = "когда в баню"

TRIGGER_PHRASE_PIZDA = "пизда"

# URL API для получения картинок
IMAGE_API_URL = "http://api.oboobs.ru/boobs/0/1/random"
IMAGE_BASE_URL = "http://media.oboobs.ru/"

VOWELS = "аеёиоуыэюя"
MAP = {
    "а": "хуя", "я": "хуя",
    "э": "хуе", "е": "хуе",
    "ы": "хуи", "и": "хуи",
    "о": "хуё", "ё": "хуё",
    "у": "хую", "ю": "хую",
}

def _match_case(prefix: str, word: str) -> str:
    if word.isupper():
        return prefix.upper()
    if word[:1].isupper():
        return prefix.capitalize()
    return prefix

def insultify_word(word: str, use_yo: bool = True) -> str:
    idx = None
    for i, ch in enumerate(word):
        lo = ch.lower()
        if lo in VOWELS:
            idx = i
            v = lo
            break
    if idx is None:
        return word

    prefix = MAP[v]
    if not use_yo and v in ("о", "ё"):
        prefix = "хуе"

    prefix = _match_case(prefix, word)
    rest = word[idx+1:]
    return prefix + rest

WORD_RE = re.compile(r"[А-Яа-яЁё]+")

def insultify_last_word(text: str, use_yo: bool = True) -> str:
    last_match = None
    for m in WORD_RE.finditer(text):
        last_match = m
    if not last_match:
        return text
    w = last_match.group(0)
    new_w = insultify_word(w, use_yo=use_yo)
    return new_w + text[last_match.end():]


def get_random_boobs_url():
    """Делает запрос к API и возвращает URL картинки."""
    try:
        response = requests.get(IMAGE_API_URL)
        response.raise_for_status()
        
        data = response.json()
        if data:
            image_path = data[0]['preview']
            full_url = IMAGE_BASE_URL + image_path
            return full_url
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к API картинок: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Неожиданный формат ответа от API: {e}")
        
    return None

quotes_cache = []

def get_random_quote():
    """Загружает цитаты из файла (если нужно) и возвращает случайную."""
    global quotes_cache
    # Если кэш пуст, читаем файл
    if not quotes_cache:
        try:
            with open('quotes.txt', 'r', encoding='utf-8') as f:
                # Читаем весь файл и делим по нашему специальному разделителю
                quotes_cache = f.read().split('\n%%%\n')
            logger.info(f"Загружено в кэш {len(quotes_cache)} цитат.")
        except FileNotFoundError:
            logger.error("Файл quotes.txt не найден!")
            return "Ой, я потерял свои цитаты. :("
    
    # Выбираем случайную цитату из кэша
    return random.choice(quotes_cache)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я на страже хорошего настроения. 😉"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения и реагирует на триггер-фразы."""
    if not update.message or not update.message.text or update.message.from_user.is_bot:
        return
         # <-- НАЧАЛО НОВОГО БЛОКА: Сбор статистики -->
    user = update.message.from_user
    update_user_stats(user.id, user.username, update.message.text)
    # <-- КОНЕЦ НОВОГО БЛОКА -->    
    message_text = update.message.text.lower().strip()
    
    
    ## ИЗМЕНЕНО: Добавляем проверку на вторую фразу через elif (else if)
    if TRIGGER_PHRASE_BOOBS in message_text:
        logger.info(f"Триггер 'сиськи' сработал в чате {update.message.chat.id}")
        
        image_url = get_random_boobs_url()
        
        if image_url:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
        else:
            await update.message.reply_text("Не смог найти картинку, попробуй еще раз позже.")
    
    ## ДОБАВЛЕНО: Новый блок для обработки второй триггер-фразы
    elif TRIGGER_PHRASE_DICK in message_text:
        logger.info(f"Триггер 'член' сработал в чате {update.message.chat.id}")
        await update.message.reply_text("Ти пидор, да ?")

    elif TRIGGER_PHRASE_PIZDA in message_text:
        logger.info(f"Триггер 'пизда' сработал в чате {update.message.chat.id}")
        await update.message.reply_text("ну и да")
        
    elif TRIGGER_PHRASE_BASH in message_text:
        logger.info(f"Триггер 'ржака' сработал в чате {update.message.chat.id}")
        quote = get_random_quote()
        await update.message.reply_text(quote)

    elif TRIGGER_PHRASE_BANYA in message_text:
        await update.message.reply_text("джуджулка выросла что ли? похвастаться хочешь?")

    elif random.random() < 0.2:
         await update.message.reply_text(insultify_last_word(message_text, use_yo=True))

def update_user_stats(user_id, username, message_text):
    """Обновляет месячную и годовую статистику пользователя в БД."""
    username = username or f"User_{user_id}"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO user_stats (user_id, username) VALUES (?, ?)", (user_id, username))


    # Проверяем, есть ли пользователь в базе
    cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        # Если нет - добавляем
        cursor.execute("INSERT INTO user_stats (user_id, username) VALUES (?, ?)", (user_id, username))

    # Обновляем счетчики
    cursor.execute("""
        UPDATE user_stats SET
        username = ?,
        message_count_monthly = message_count_monthly + 1,
        message_count_yearly = message_count_yearly + 1,
        total_chars_count_monthly = total_chars_count_monthly + ?,
        total_chars_count_yearly = total_chars_count_yearly + ?
        WHERE user_id = ?
    """, (username, len(message_text), len(message_text), user_id))

    # Считаем маты
    swear_found_count = sum([1 for word in SWEAR_WORDS if word in message_text.lower()])
    if swear_found_count > 0:
        cursor.execute("""
            UPDATE user_stats SET 
            swear_count_monthly = swear_count_monthly + ?,
            swear_count_yearly = swear_count_yearly + ?
            WHERE user_id = ?
        """, (swear_found_count, swear_found_count, user_id))
        
    # Считаем запросы сисек
    if TRIGGER_PHRASE_BOOBS in message_text.lower():
        cursor.execute("""
            UPDATE user_stats SET 
            boobs_request_count_monthly = boobs_request_count_monthly + 1,
            boobs_request_count_yearly = boobs_request_count_yearly + 1
            WHERE user_id = ?
        """, (user_id,))
    
    conn.commit()
    conn.close()
    
## ДОБАВИТЬ ЭТИ ДВЕ ФУНКЦИИ
def generate_stats_report(period: str) -> str:
    """Генерирует текст отчета для заданного периода ('monthly' или 'yearly')."""
    if period not in ['monthly', 'yearly']:
        return "Неверный период для статистики."

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Динамически подставляем нужные колонки
    msg_col, swear_col, boobs_col, chars_col = (f"message_count_{period}", f"swear_count_{period}", 
                                               f"boobs_request_count_{period}", f"total_chars_count_{period}")

    cursor.execute(f"SELECT username, {msg_col} FROM user_stats WHERE {msg_col} > 0 ORDER BY {msg_col} ASC LIMIT 1")
    partisan = cursor.fetchone()
    cursor.execute(f"SELECT username, {msg_col} FROM user_stats ORDER BY {msg_col} DESC LIMIT 1")
    maniac = cursor.fetchone()
    cursor.execute(f"SELECT username, {swear_col} FROM user_stats ORDER BY {swear_col} DESC LIMIT 1")
    boatswain = cursor.fetchone()
    cursor.execute(f"SELECT username, {boobs_col} FROM user_stats ORDER BY {boobs_col} DESC LIMIT 1")
    connoisseur = cursor.fetchone()
    cursor.execute(f"SELECT username, CAST({chars_col} AS REAL) / {msg_col} FROM user_stats WHERE {msg_col} > 0 ORDER BY CAST({chars_col} AS REAL) / {msg_col} DESC LIMIT 1")
    tolstoy = cursor.fetchone()

    conn.close()
    
    title = "Статистика Месяца!" if period == 'monthly' else "Итоги Года!"
    report = f"🏆 **{title}** 🏆\n\n"
    if maniac: report += f"🏅 **Клавиатурный маньяк**: @{maniac[0]} (сообщений: {maniac[1]})\n"
    if partisan: report += f"🎖️ **Партизан {('месяца' if period == 'monthly' else 'года')}**: @{partisan[0]} (сообщений: {partisan[1]})\n"
    if boatswain and boatswain[1] > 0: report += f"🤬 **Боцман чата**: @{boatswain[0]} (ругательств: {boatswain[1]})\n"
    if connoisseur and connoisseur[1] > 0: report += f"🧐 **Верховный ценитель**: @{connoisseur[0]} (запросов: {connoisseur[1]})\n"
    if tolstoy: report += f"✍️ **Лев Толстой**: @{tolstoy[0]} (ср. длина сообщ.: {tolstoy[1]:.0f} симв.)\n"

    return report

async def post_monthly_report(context: ContextTypes.DEFAULT_TYPE):
    """Публикует месячный отчет, переносит данные в годовой и сбрасывает месяц."""
    logger.info("Начало ежемесячной задачи: публикация отчета.")
    report_text = generate_stats_report('monthly')
    report_text += "\n\nНачинаем новый месяц! Статистика за этот месяц сброшена."
    await context.bot.send_message(chat_id=CHAT_ID_FOR_STATS, text=report_text, parse_mode='Markdown')
    
    # Агрегируем и сбрасываем статистику
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Сброс
    cursor.execute("""
        UPDATE user_stats SET 
        message_count_monthly = 0, swear_count_monthly = 0, 
        boobs_request_count_monthly = 0, total_chars_count_monthly = 0
    """)
    conn.commit()
    conn.close()
    logger.info("Ежемесячная статистика сброшена.")

async def post_yearly_report(context: ContextTypes.DEFAULT_TYPE):
    """Публикует годовой отчет."""
    # Проверка, что сегодня действительно 31 декабря
    now = datetime.datetime.now(TIMEZONE)
    if now.month == 12 and now.day == 31:
        logger.info("Начало ежегодной задачи: публикация отчета.")
        report_text = generate_stats_report('yearly')
        report_text += "\n\nС наступающим Новым Годом! 🥳"
        await context.bot.send_message(chat_id=CHAT_ID_FOR_STATS, text=report_text, parse_mode='Markdown')

async def send_stats_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет отчет по статистике чата."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- Получаем победителей в номинациях ---
    # Партизан (меньше всех сообщений, но хотя бы одно)
    cursor.execute("SELECT username, message_count FROM user_stats WHERE message_count > 0 ORDER BY message_count ASC LIMIT 1")
    partisan = cursor.fetchone()
    # Клавиатурный маньяк
    cursor.execute("SELECT username, message_count FROM user_stats ORDER BY message_count DESC LIMIT 1")
    maniac = cursor.fetchone()
    # Боцман
    cursor.execute("SELECT username, swear_count FROM user_stats ORDER BY swear_count DESC LIMIT 1")
    boatswain = cursor.fetchone()
    # Ценитель прекрасного
    cursor.execute("SELECT username, boobs_request_count FROM user_stats ORDER BY boobs_request_count DESC LIMIT 1")
    connoisseur = cursor.fetchone()
    # Лев Толстой
    cursor.execute("SELECT username, CAST(total_chars_count AS REAL) / message_count FROM user_stats WHERE message_count > 0 ORDER BY CAST(total_chars_count AS REAL) / message_count DESC LIMIT 1")
    tolstoy = cursor.fetchone()

    conn.close()

    # --- Формируем красивый отчет ---
    report = "🏆 **Статистика Месяца!** 🏆\n\n"
    if maniac:
        report += f"🏅 **Клавиатурный маньяк**: @{maniac[0]} (сообщений: {maniac[1]})\n"
    if partisan:
        report += f"🎖️ **Партизан месяца**: @{partisan[0]} (сообщений: {partisan[1]})\n"
    if boatswain and boatswain[1] > 0:
        report += f"🤬 **Боцман чата**: @{boatswain[0]} (ругательств: {boatswain[1]})\n"
    if connoisseur and connoisseur[1] > 0:
        report += f"🧐 **Верховный ценитель прекрасного**: @{connoisseur[0]} (запросов: {connoisseur[1]})\n"
    if tolstoy:
        report += f"✍️ **Лев Толстой этого чата**: @{tolstoy[0]} (ср. длина сообщ.: {tolstoy[1]:.0f} симв.)\n"

    report += "\nПродолжаем в том же духе! Статистика сбросится в начале месяца (на самом деле когда админ напишет /resetstats 😉)."
    await update.message.reply_text(report, parse_mode='Markdown')

## ИЗМЕНИТЬ
async def reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... проверка на админа ...
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Обнуляем ВСЕ счетчики
    cursor.execute("""
        UPDATE user_stats SET 
        message_count_monthly = 0, swear_count_monthly = 0, boobs_request_count_monthly = 0, total_chars_count_monthly = 0,
        message_count_yearly = 0, swear_count_yearly = 0, boobs_request_count_yearly = 0, total_chars_count_yearly = 0
    """)
    conn.commit()
    conn.close()
    
    await update.message.reply_text("✅ Внимание! ВСЯ статистика (месячная и годовая) полностью обнулена!")

def main() -> None:
    """Основная функция для запуска бота и планировщика."""
    if not TOKEN:
        logger.error("Токен не найден!")
        return

    application = Application.builder().token(TOKEN).build()
    
    # Получаем очередь задач
    job_queue = application.job_queue

    # --- НАСТРОЙКА ПЛАНИРОВЩИКА ---
    # Задача для ежемесячного отчета: 1-го числа каждого месяца в 14:00
    job_queue.run_monthly(post_monthly_report, day=1, time=datetime.time(hour=14, minute=0, tzinfo=TIMEZONE))
    
    # Задача для ежегодного отчета: запускается каждый день в 20:00, но выполняет действие только 31 декабря
    job_queue.run_daily(post_yearly_report, time=datetime.time(hour=20, minute=0, tzinfo=TIMEZONE))
    
    logger.info("Планировщик задач настроен.")

    # ... регистрация всех твоих CommandHandler и MessageHandler ...
    application.add_handler(CommandHandler("start", start))
    # и так далее
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()


if __name__ == '__main__':
    main()
