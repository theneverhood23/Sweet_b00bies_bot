
import logging
import requests

logger = logging.getLogger(__name__)

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
