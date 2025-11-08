
import logging
import random

logger = logging.getLogger(__name__)
quotes_cache = []

def Get_random_quote():
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
