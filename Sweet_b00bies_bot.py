import os
import logging
import random
import bash_quote
import boobs
import insultify_last_word
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
TRIGGER_PHRASE_DICK = "скинь член"
TRIGGER_PHRASE_BASH = "скинь ржаку"
TRIGGER_PHRASE_BANYA = "когда в баню"
TRIGGER_PHRASE_ASS = "скинь попку"

# URL API для получения картинок

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
    
    if TRIGGER_PHRASE_BOOBS in message_text:
        image_url = boobs.get_random_boobs_url()
        
        if image_url:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
        else:
            await update.message.reply_text("Не смог найти картинку, попробуй еще раз позже.")
    
    ## ДОБАВЛЕНО: Новый блок для обработки второй триггер-фразы
    elif TRIGGER_PHRASE_DICK in message_text:
        await update.message.reply_text("Ти пидор, да ?")

    elif TRIGGER_PHRASE_BASH in message_text:
        quote = bash_quote.Get_random_quote()
        await update.message.reply_text(quote)

    elif TRIGGER_PHRASE_BANYA in message_text:
        await update.message.reply_text("джуджулка выросла что ли? похвастаться хочешь?")

    elif TRIGGER_PHRASE_ASS in message_text:
        await update.message.reply_text("ты ебобо? мож тебе еще денег скинуть на карту?")

    elif "хде я" in message_text:
        await update.message.reply_text(update.message.chat_id)

    elif "хто я" in message_text:
        await update.message.reply_text(update.message.from_user.full_name)
    
    elif random.random() < 0.2:
        await update.message.reply_text(insultify_last_word.insultify_last_word(message_text, use_yo=True))


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
