import os
import logging
import requests
import re
import random
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

# Триггер-фразы, на которые будет реагировать бот (приводим к нижнему регистру)
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
    if not update.message or not update.message.text:
        return
        
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
        quote = re.sub(r"(?i)<br\s*/?>", "**", quote)
        await update.message.reply_text(quote)

    elif TRIGGER_PHRASE_BANYA in message_text:
        await update.message.reply_text("джуджулка выросла что ли? похвастаться хочешь?")

    elif random.random() < 0.2:
         await update.message.reply_text(insultify_last_word(message_text, use_yo=True))


def main() -> None:
    """Основная функция для запуска бота."""
    if not TOKEN:
        logger.error("Токен не найден! Проверьте файл .env и переменную TELEGRAM_TOKEN.")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()
