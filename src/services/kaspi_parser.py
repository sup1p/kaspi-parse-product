from src.utils import (
    remove_general_if_duplicate,
    parse_price,
    extract_product_id_from_url,
    extract_city_id_from_url,
    PRICE_RE
    )
from logs.config_logs import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional

import requests
import time
import re



def parse_kaspi_product_with_bs(url: str, headless: bool = True, wait_seconds: int = 5) -> Dict[str, Any]:
    
    result: Dict[str, Any] = {
        "url": url,
        "name": None,
        "category": None,
        "price_min": None,
        "price_max": None,
        "rating": None,
        "reviews_count": None,
        "images": [],
        "attributes": {},
        "fetched_at": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        # можно установить UA если нужно:
        page.set_extra_http_headers({"Accept-Language": "ru-RU,ru;q=0.9"})

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_selector("h1", timeout=10000)
            except PlaywrightTimeoutError:
                # fallback: подождём небольшую паузу, чтобы JS успел отрисоваться
                page.wait_for_timeout(2000)

            # Дополнительное ожидание networkidle для более сложных страниц
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except PlaywrightTimeoutError:
                # если networkidle не наступил — продолжаем: у нас уже есть HTML
                pass

            html = page.content()
            result["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        finally:
            browser.close()

    # Парсим с помощью BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # NAME: обычно в h1
    h1 = soup.find("h1")
    if h1:
        result["name"] = h1.get_text(strip=True)


    # PRICE: ищем элементы, содержащие символ валюты (₸) или классы с price
    price_candidates = []
    for sel in ["span[itemprop='price']", ".price", ".item__price", ".product-price", ".product__price", ".price__main"]:
        for t in soup.select(sel):
            txt = t.get_text(" ", strip=True)
            if "₸" in txt or re.search(PRICE_RE, txt):
                price_candidates.append(txt)
    # fallback: любой текст страницы с ₸
    if not price_candidates:
        text_all = soup.get_text(" ")
        for m in re.finditer(r"[\d\s]{2,}\s*₸", text_all):
            price_candidates.append(m.group(0))


    # IMAGES: ищем теги <img> внутри галереи, фильтруем по http
    imgs = set()
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy")
        if src and src.startswith("http"):
            imgs.add(src.split("?")[0])
    result["images"] = list(imgs)

    attributes = {}

    # 1) Собираем все группы спецификаций (если есть)
    parsed_groups = []  # list of (group_name, {key: val})
    for group in soup.select("div.specifications__group"):
        group_name_tag = group.select_one("h3")
        group_name = group_name_tag.get_text(strip=True) if group_name_tag else "Общие"

        # Собираем пары dt/dd внутри группы
        keys = group.select("dt")
        vals = group.select("dd")
        group_attrs: Dict[str, str] = {}
        for dt, dd in zip(keys, vals):
            key = dt.get_text(strip=True)
            val = dd.get_text(" ", strip=True)  # пробел между внутренними элементами
            if key:
                group_attrs[key] = val

        if group_attrs:
            parsed_groups.append((group_name, group_attrs))

    # 2) Фоллбек: отдельные dl dt/dd по всей странице (плоская структура)
    fallback_attrs: Dict[str, str] = {}
    for dt, dd in zip(soup.select("dl dt"), soup.select("dl dd")):
        key = dt.get_text(strip=True)
        val = dd.get_text(" ", strip=True)
        if key:
            fallback_attrs[key] = val

    # 3) Сначала добавляем все группы, кроме тех, которые названы как "Общие" (или похожие)
    for group_name, group_attrs in parsed_groups:
        name_lower = (group_name or "").lower()
        if name_lower.startswith("общ"):  # 'общие', 'Общие' и т.п. — отложим на потом
            continue
        attributes[group_name] = group_attrs

    # 4) Собираем множество всех ключей, которые уже добавлены
    existing_keys = set()
    for g in attributes.values():
        existing_keys.update(g.keys())
    existing_keys.update(fallback_attrs.keys())  # учитываем fallback тоже

    # 6) Если у нас нет ни одной группы, но есть fallback — используем его
    if not attributes and fallback_attrs:
        attributes = fallback_attrs.copy()
    else:
        # 7) Добавляем оставшиеся ключи из fallback в секцию "Другие" (только те, которых ещё нет)
        for k, v in fallback_attrs.items():
            if k in existing_keys:
                continue
            attributes.setdefault("Другие", {})[k] = v

    result["attributes"] = attributes

    rating_data = parse_kaspi_rating_playwright(url)

    if rating_data:
        result["rating"] = rating_data.get("rating")
        result["reviews_count"] = rating_data.get("reviews_count")
        
    offers_data = fetch_offers(url=url)
    
    if offers_data:
        result["price_min"] = min(offer["price"] for offer in offers_data if offer["price"] is not None)
        result["price_max"] = max(offer["price"] for offer in offers_data if offer["price"] is not None)
        result["offers_amount"] = len(offers_data)
        result["offers"] = offers_data
        
    category_path = get_category_path(url=url)
    
    if category_path:
        result["category"] = category_path
    
    attributes = remove_general_if_duplicate(attributes)
    
    if attributes:
        result["attributes"] = attributes
        
    
    return result
        
        
def fetch_offers(url: str, max_retries: int = 3) -> List[Dict[str, Any]]:
    product_id = extract_product_id_from_url(url)
    city_id = extract_city_id_from_url(url)

    api_url = f"https://kaspi.kz/yml/offer-view/offers/{product_id}"
    product_url = url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": product_url,
        "Origin": "https://kaspi.kz",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
    }

    session = requests.Session()
    session.headers.update(headers)

    # Получаем cookies для обхода 403
    try:
        session.get(product_url, timeout=10)
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении cookies: {e}")
        return []

    all_offers = []
    page = 0
    limit = 50
    
    while True:
        payload = {
            "cityId": city_id,  # Алматы
            "limit": limit,
            "page": page,
            "sort": True
        }

        # Retry логика для каждого запроса
        response = None
        for attempt in range(max_retries):
            try:
                response = session.post(api_url, json=payload, timeout=15)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:  # Too Many Requests
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Rate limit, ждем {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    logger.info(f"HTTP {response.status_code} на странице {page}, попытка {attempt + 1}")
                    time.sleep(1)
            except requests.RequestException as e:
                logger.info(f"Ошибка запроса на странице {page}, попытка {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)

        if not response or response.status_code != 200:
            logger.info(f"Не удалось получить данные для страницы {page} после {max_retries} попыток")
            break

        try:
            data = response.json()
        except Exception as e:
            logger.info(f"Ошибка при разборе JSON на странице {page}: {e}")
            break

        offers = data.get("offers", [])
        
        if not offers:
            logger.info(f"Страница {page}: офферы не найдены, завершаем")
            break
            
        logger.info(f"Страница {page}: найдено {len(offers)} офферов")
        
        # Обрабатываем офферы и добавляем в общий список
        for offer in offers:
            price_value = offer.get("price")
            if isinstance(price_value, dict):
                price = price_value.get("amount")
            else:
                price = price_value
            
            processed_offer = {
                "merchant_name": offer.get("merchantName", "Unknown"),
                "price": price
            }
                
            all_offers.append(processed_offer)

        # Проверяем, нужно ли загружать следующую страницу
        if len(offers) < limit:
            logger.info(f"Получено офферов меньше лимита ({len(offers)} < {limit}), это последняя страница")
            break
            
        page += 1
        
        # Небольшая пауза между запросами чтобы не нагружать сервер
        time.sleep(0.5)

    logger.info(f"Всего собрано {len(all_offers)} офферов")
    return all_offers
        
        
def parse_kaspi_rating_playwright(url: str, max_retries: int = 3) -> Dict[str, Optional[float]]:
    logger.info(f"Начинаем парсинг рейтинга: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=60000)
            logger.info("Страница загружена, ищем рейтинг...")
        except Exception as e:
            logger.info(f"Ошибка при загрузке страницы: {e}")
            browser.close()
            return {"rating": None, "reviews_count": None}
        
        # Пытаемся найти рейтинг несколько раз
        for attempt in range(max_retries):
            logger.info(f"Попытка {attempt + 1}/{max_retries}")
            
            try:
                # Ждем появления блока с рейтингом
                try:
                    page.wait_for_selector(".item__rating", timeout=5000)
                    logger.info("  ✓ Селектор .item__rating найден")
                except PlaywrightTimeoutError:
                    logger.info("  ✗ Селектор .item__rating не найден за 5 сек")
                    if attempt < max_retries - 1:
                        logger.info("  Пауза 2 сек перед следующей попыткой...")
                        time.sleep(2)
                        continue
                    else:
                        logger.info("  Последняя попытка - пробуем парсить имеющийся HTML")

                # Получаем HTML и парсим
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                rating_block = soup.select_one(".item__rating")

                if not rating_block:
                    logger.info(f"  ✗ Блок .item__rating не найден в HTML")
                    if attempt < max_retries - 1:
                        logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                        time.sleep(2)
                        continue
                    else:
                        break

                logger.info(f"  ✓ Блок рейтинга найден, парсим данные...")

                # Ищем span с классом rating _X
                span_rating = rating_block.select_one('span[class*="rating _"]')
                rating_value = None
                
                if span_rating:
                    class_list = span_rating.get('class', [])
                    match = re.search(r'_(\d+)', ' '.join(class_list))
                    if match:
                        rating_value = int(match.group(1))
                        logger.info(f"  ✓ Рейтинг найден: {rating_value}")
                    else:
                        logger.info(f"  ✗ Не удалось извлечь рейтинг из классов: {class_list}")
                else:
                    logger.info(f"  ✗ Span с рейтингом не найден")

                # Количество отзывов
                reviews_link = rating_block.select_one(".item__rating-link span")
                reviews_count = None
                
                if reviews_link:
                    reviews_text = reviews_link.get_text(strip=True)
                    match = re.search(r"(\d+)", reviews_text)
                    if match:
                        reviews_count = int(match.group(1))
                        logger.info(f"  ✓ Количество отзывов найдено: {reviews_count}")
                    else:
                        logger.info(f"  ✗ Не удалось извлечь число отзывов из текста: '{reviews_text}'")
                else:
                    logger.info(f"  ✗ Ссылка на отзывы не найдена")

                # Если хотя бы что-то нашли - возвращаем результат
                if rating_value is not None or reviews_count is not None:
                    logger.info(f"  ✓ Парсинг успешен на попытке {attempt + 1}")
                    browser.close()
                    return {"rating": rating_value/10, "reviews_count": reviews_count}
                else:
                    logger.info(f"  ✗ Ни рейтинг, ни отзывы не найдены")
                    if attempt < max_retries - 1:
                        logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                        time.sleep(2)
                    
            except Exception as e:
                logger.info(f"  ✗ Ошибка на попытке {attempt + 1}: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                    time.sleep(2)

        logger.info(f"✗ Все {max_retries} попыток неудачны, возвращаем пустой результат")
        browser.close()
        return {"rating": None, "reviews_count": None}
    
    
def get_category_path(url: str, max_retries: int = 3, timeout: int = 10) -> Optional[str]:
    logger.info(f"Начинаем получение категории для URL: {url}")
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    for attempt in range(max_retries):
        logger.info(f"Попытка {attempt + 1}/{max_retries} получения категории")
        
        try:
            # Делаем запрос с таймаутом
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                logger.info("  ✓ HTTP 200 - страница загружена")
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Ищем хлебные крошки с различными селекторами
                selectors_to_try = [
                    "div.breadcrumbs a.breadcrumbs__item",
                    ".breadcrumbs a",
                    "nav.breadcrumbs a", 
                    ".breadcrumbs__item",
                    "a.breadcrumbs__link",
                    ".breadcrumb a"
                ]
                
                breadcrumbs = []
                for selector in selectors_to_try:
                    breadcrumbs = soup.select(selector)
                    if breadcrumbs:
                        logger.info(f"  ✓ Хлебные крошки найдены с селектором: {selector}")
                        break
                    else:
                        logger.info(f"  - Селектор '{selector}' не дал результатов")
                
                if not breadcrumbs:
                    logger.info(f"  ✗ Хлебные крошки не найдены ни одним из селекторов")
                    if attempt < max_retries - 1:
                        logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                        time.sleep(2)
                        continue
                    else:
                        logger.info(f"  Последняя попытка - возвращаем None")
                        return None
                
                category_items = []
                for a in breadcrumbs:
                    text = a.get_text(strip=True)
                    if text and text.lower() not in ['главная', 'home', 'kaspi.kz']:
                        category_items.append(text)
                
                if category_items:
                    category_path = " > ".join(category_items)
                    logger.info(f"  ✓ Путь категории успешно извлечен: '{category_path}'")
                    return category_path
                else:
                    logger.info(f"  ✗ Все элементы хлебных крошек пустые или нерелевантные")
                    if attempt < max_retries - 1:
                        logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                        time.sleep(2)
                        continue
                        
            elif response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"  ✗ HTTP 429 (Rate limit) - ждем {wait_time} секунд...")
                time.sleep(wait_time)
                continue
                
            elif response.status_code in [403, 503]:  # Forbidden или Service Unavailable
                logger.info(f"  ✗ HTTP {response.status_code} - возможно блокировка")
                if attempt < max_retries - 1:
                    wait_time = 3 + attempt  # Увеличиваем задержку
                    logger.info(f"  Пауза {wait_time} сек перед следующей попыткой...")
                    time.sleep(wait_time)
                    continue
                    
            else:
                logger.info(f"  ✗ HTTP {response.status_code} - неожиданный код ответа")
                if attempt < max_retries - 1:
                    logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                    time.sleep(2)
                    continue
                    
        except requests.exceptions.Timeout:
            logger.info(f"  ✗ Таймаут ({timeout}с) на попытке {attempt + 1}")
            if attempt < max_retries - 1:
                logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                time.sleep(2)
                
        except requests.exceptions.ConnectionError as e:
            logger.info(f"  ✗ Ошибка соединения на попытке {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"  Пауза 3 сек перед следующей попыткой...")
                time.sleep(3)
                
        except requests.exceptions.RequestException as e:
            logger.info(f"  ✗ Ошибка запроса на попытке {attempt + 1}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                time.sleep(2)
                
        except Exception as e:
            logger.info(f"  ✗ Неожиданная ошибка на попытке {attempt + 1}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"  Пауза 2 сек перед следующей попыткой...")
                time.sleep(2)
    
    logger.info(f"✗ Все {max_retries} попыток неудачны, возвращаем None")
    return None
