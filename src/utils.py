from typing import Optional
from urllib.parse import urlparse, parse_qs
import re
import logging

logger = logging.getLogger(__name__)

PRICE_RE = re.compile(r"[\d\s]+")  # для извлечения чисел из текста цены


def remove_general_if_duplicate(attributes: dict) -> dict:
    """
    Убирает дублирующиеся данные из словаря атрибутов.
    
    Удаляет ключи-группы (например, "Фотокамера и мультимедиа"), если их содержимое
    дублируется в отдельных детализированных ключах.
    
    Args:
        attributes: Словарь атрибутов товара
    
    Returns:
        Очищенный от дублей словарь
    """
    if not isinstance(attributes, dict) or not attributes:
        return attributes

    logger.info(f"Начинаем очистку от дубликатов. Исходное количество ключей: {len(attributes)}")
    
    # Создаем копию для безопасной работы
    cleaned_attributes = attributes.copy()
    
    # Собираем отдельные ключи (не групповые)
    individual_keys = set()
    group_keys = []
    
    for key, value in attributes.items():
        if isinstance(value, str) and len(value) > 100:
            # Длинные строки скорее всего группы со сводной информацией
            group_keys.append(key)
        elif key and key.strip().endswith(':'):
            # Ключи с двоеточием обычно отдельные параметры
            individual_keys.add(key.strip(':').strip())
        else:
            # Обычные отдельные ключи
            individual_keys.add(key)
    
    logger.info(f"Найдено отдельных ключей: {len(individual_keys)}")
    logger.info(f"Найдено групповых ключей: {len(group_keys)}")
    
    # Проверяем каждую группу на дубликаты
    keys_to_remove = set()
    
    for group_key in group_keys:
        group_value = str(attributes[group_key])
        logger.info(f"\nАнализируем группу: '{group_key}'")
        
        # Подсчитываем сколько отдельных ключей содержится в тексте группы
        found_keys = []
        
        for individual_key in individual_keys:
            if not individual_key or individual_key == group_key:
                continue
                
            # Очищаем ключ от лишних символов для поиска
            clean_key = individual_key.strip().rstrip(':')
            
            # Ищем ключ в тексте группы различными способами
            if _key_found_in_text(clean_key, group_value):
                found_keys.append(individual_key)
        
        # Если в группе найдено много отдельных ключей - это дубликат
        if len(found_keys) >= 3:  # Порог: если 3+ ключа найдены в тексте группы
            logger.info(f"  ✗ Группа '{group_key}' содержит {len(found_keys)} отдельных ключей: {found_keys[:5]}...")
            keys_to_remove.add(group_key)
        else:
            logger.info(f"  ✓ Группа '{group_key}' уникальна (найдено ключей: {len(found_keys)})")
    
    # Также удаляем ключи "Общие" и похожие
    general_keys = [k for k in attributes.keys() if k and 'общ' in k.lower()]
    keys_to_remove.update(general_keys)
    
    if general_keys:
        logger.info(f"\nУдаляем общие ключи: {general_keys}")
    
    # Удаляем найденные дубликаты
    for key in keys_to_remove:
        cleaned_attributes.pop(key, None)
    
    logger.info(f"\nРезультат: удалено {len(keys_to_remove)} ключей, осталось {len(cleaned_attributes)}")
    if keys_to_remove:
        logger.info(f"Удаленные ключи: {list(keys_to_remove)}")
    
    return cleaned_attributes


def _key_found_in_text(key: str, text: str) -> bool:
    """
    Проверяет, содержится ли ключ в тексте различными способами.
    
    Args:
        key: Ключ для поиска
        text: Текст для поиска
        
    Returns:
        True если ключ найден
    """
    if not key or not text:
        return False
    
    key_lower = key.lower()
    text_lower = text.lower()
    
    # Точное совпадение
    if key_lower in text_lower:
        return True
    
    # Поиск как отдельное слово
    words_in_text = text_lower.split()
    key_words = key_lower.split()
    
    # Если ключ состоит из одного слова
    if len(key_words) == 1:
        return key_lower in words_in_text
    
    # Если ключ состоит из нескольких слов - ищем последовательность
    key_phrase = ' '.join(key_words)
    return key_phrase in text_lower


def parse_price(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    s = text.replace('\xa0', ' ').strip()
    m = PRICE_RE.search(s)
    if not m:
        return None
    try:
        return float(m.group(0).replace(" ", ""))
    except Exception:
        return None

def extract_product_id_from_url(url: str):
    match_product = re.search(r'/p/[^/]+-(\d+)', url)
    product_id = match_product.group(1)
    
    return product_id
    
def extract_city_id_from_url(url: str):
    match_city = re.search(r'[?&]c=(\d+)', url)
    city_id = match_city.group(1) # if match_city else "750000000"  # Алматы по умолчанию
    return city_id



def is_valid_kaspi_url(url: str) -> bool:
    """
    Проверяет, что ссылка Kaspi.kz валидна и содержит:
      - product_id в формате /p/...-123456789/
      - параметр ?c=750000000 (число)
    Возвращает True, если всё ок, иначе False.
    """
    try:
        parsed = urlparse(url)

        # Проверяем домен
        if "kaspi.kz" not in parsed.netloc.lower():
            return False

        # Проверяем product_id в пути
        if not re.search(r'/p/[^/]+-(\d+)(?:/)?$', parsed.path):
            return False

        # Проверяем city_id в query (?c=...)
        qs = parse_qs(parsed.query)
        c = qs.get("c", [None])[0]
        if not (c and c.isdigit()):
            return False

        return True
    except Exception:
        return False
