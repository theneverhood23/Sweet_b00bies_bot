import os
import logging
import requests
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


# URL API для получения картинок
IMAGE_API_URL = "http://api.oboobs.ru/boobs/0/1/random"
IMAGE_BASE_URL = "http://media.oboobs.ru/"

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
        await update.message.reply_text("Ти пидор, да?")


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
