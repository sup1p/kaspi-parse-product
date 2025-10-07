# Kaspi Parser - Python Backend для анализа товаров на Kaspi.kz

## О проекте

Kaspi Parser - это веб-сервис для парсинга и анализа товаров с маркетплейса Kaspi.kz. Проект создан как решение тестового задания для команды VR TECH и предназначен для создания платформы аналитики продавцов на маркетплейсах.

### Основной функционал
- Парсинг карточек товаров с Kaspi.kz
- Сбор информации о ценах, рейтингах, характеристиках
- Сбор данных об офферах продавцов
- Сохранение данных в PostgreSQL
- Экспорт данных в JSON формате
- RESTful API для управления данными
- Логирование в JSON формате

## Технологический стек

### Backend
- **Python 3.13+** - основной язык разработки
- **FastAPI** - веб-фреймворк для создания API
- **Uvicorn** - ASGI сервер
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **Alembic** - инструмент для миграций БД
- **Pydantic** - валидация данных и типизация

### База данных
- **PostgreSQL 15** - основная база данных
- **Asyncpg** - асинхронный драйвер для PostgreSQL

### Парсинг
- **Playwright** - автоматизация браузера
- **BeautifulSoup4** - парсинг HTML
- **Requests** - HTTP-клиент
- **HTTPX** - асинхронный HTTP-клиент

### Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **UV** - современный менеджер пакетов Python
- **Tenacity** - повторные попытки при ошибках

### Логирование
- **Python JSON Logger** - структурированное логирование

## Структура проекта

```
tzvr/
├── 📄 README.md                    # Документация проекта
├── 📄 pyproject.toml              # Конфигурация Python проекта
├── 📄 uv.lock                     # Замороженные зависимости
├── 📄 seed.json                   # Исходные URL для парсинга
├── 📄 docker-compose.yml          # Конфигурация Docker
├── 📄 Dockerfile                  # Образ приложения
├── 📄 entrypoint.sh               # Скрипт запуска в контейнере
├── 📄 alembic.ini                 # Конфигурация миграций
├── 📄 main.py                     # Точка входа приложения
│
├── 📁 src/                        # Исходный код приложения
│   ├── 📄 __init__.py
│   ├── 📄 main.py                 # FastAPI приложение
│   ├── 📄 models.py               # SQLAlchemy модели
│   ├── 📄 schemas.py              # Pydantic схемы
│   ├── 📄 crud.py                 # CRUD операции
│   ├── 📄 tasks.py                # Фоновые задачи
│   ├── 📄 utils.py                # Утилиты
│   │
│   ├── 📁 core/                   # Основные компоненты
│   │   ├── 📄 config.py           # Конфигурация приложения
│   │   ├── 📄 database.py         # Подключение к БД
│   │   └── 📄 dependencies.py     # Зависимости FastAPI
│   │
│   ├── 📁 routers/                # API маршруты
│   │   ├── 📄 api_v1.py           # API версии 1
│   │   ├── 📄 health.py           # Проверка здоровья сервиса
│   │   └── 📄 products.py         # API для работы с товарами
│   │
│   └── 📁 services/               # Бизнес-логика
│       ├── 📄 kaspi_parser.py     # Парсер Kaspi.kz
│       └── 📄 file_service.py     # Работа с файлами
│
├── 📁 alembic/                    # Миграции базы данных
│   ├── 📄 env.py                  # Конфигурация Alembic
│   └── 📁 versions/               # Файлы миграций
│       └── 📄 810ee4d87216_init_models.py
│
├── 📁 export/                     # 📊 Экспортированные данные
│   ├── 📁 products/               # JSON файлы товаров
│   │   ├── 📄 product_109126670.json
│   │   ├── 📄 product_109619826.json
│   │   └── 📄 product_118366664.json
│   └── 📁 offers/                 # JSON файлы офферов продавцов
│       ├── 📄 offers_109126670.json
│       ├── 📄 offers_109619826.json
│       └── 📄 offers_118366664.json
│
├── 📁 logs/                       # 📝 Система логирования
│   ├── 📄 config_logs.py          # Конфигурация логгера
│   └── 📁 logs/                   # Файлы логов
│       └── 📄 app.log             # Основной лог файл (JSON формат)
│
└── 📁 screens/                    # 📸 Скриншоты работы системы
    ├── 📄 image.png
    ├── 📄 image1.png
    ├── 📄 image3.png
    ├── 📄 image4.png
    ├── 📄 image5.png
    └── 📄 image6.png
```

### Описание ключевых папок и файлов

#### `src/` - Основной код приложения
- **`models.py`** - Модели данных для PostgreSQL (Product, ProductOffer, ProductAttribute и др.)
- **`schemas.py`** - Pydantic схемы для валидации API
- **`crud.py`** - CRUD операции для работы с базой данных
- **`services/kaspi_parser.py`** - Основной парсер с использованием Playwright и BeautifulSoup

#### `export/` - Экспортированные данные
- **`products/`** - JSON файлы с данными о товарах (название, цена, рейтинг, характеристики)
- **`offers/`** - JSON файлы с офферами продавцов (продавец, цена)

Пример структуры данных товара:
```json
{
  "name": "Косметичка полиэстер 10.5X17 см",
  "category": "Красота и здоровье > Косметички",
  "price_min": 238.0,
  "price_max": 4500.0,
  "rating": 4.9,
  "reviews_count": 1508,
  "offers_amount": 47
}
```

#### `logs/` - Система логирования
- **`config_logs.py`** - Настройка JSON логирования
- **`logs/app.log`** - Ротируемый лог файл с событиями системы
- Логи в JSON формате для удобного анализа

#### `alembic/` - Миграции базы данных
- Система версионирования схемы БД
- Автоматическое применение изменений при запуске

## Быстрый старт

### Предварительные требования
- Python 3.13+
- UV (современный менеджер пакетов)
- Docker & Docker Compose
- PostgreSQL (при локальном запуске)

### 1️ Локальный запуск

```bash
# Клонирование репозитория
git clone <repository-url>
cd tzvr

# Установка зависимостей через UV
uv sync

# Создание файла окружения
cp .env.example .env
# Отредактировать .env с вашими настройками

# Запуск PostgreSQL локально или через Docker
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Применение миграций
uv run alembic upgrade head

# Запуск приложения
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2 Запуск через Docker Compose 🐳

```bash
# Клонирование и переход в директорию
git clone <repository-url>
cd tzvr

# Создание файла окружения
cp .env.example .env

# Запуск всех сервисов
docker-compose up --build

# Проверка логов
docker-compose logs -f app
```

Docker Compose включает:
- **PostgreSQL 15** - база данных на порту 5432
- **Kaspi Parser App** - основное приложение на порту 8000
- **Автоматические миграции** при запуске
- **Health checks** для проверки готовности сервисов

### 3 Проверка работы

После запуска доступны:
- 🌐 **API документация**: http://localhost:8000/docs
- 🔍 **Health check**: http://localhost:8000/health
- 📊 **Основное API**: http://localhost:8000/api/v1/

## Основные возможности

### Парсинг товаров

#### Быстрое тестирование
Для быстрой проверки работы парсера вы можете использовать тестовую ссылку:

**Тестовая ссылка**: https://kaspi.kz/shop/p/kosmetichka-poliester-10-5x17-sm-109126670/?c=750000000

Вы можете опробовать ее в ручном режиме через POST запрос к эндпоинту `/parser/scrape-props`:

```bash
# Тестирование парсера с готовой ссылкой
curl -X POST "http://localhost:8000/parser/scrape-props" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://kaspi.kz/shop/p/kosmetichka-poliester-10-5x17-sm-109126670/?c=750000000"}'
```

#### Общий парсинг товаров
```bash
# Парсинг товара по URL
curl -X POST "http://localhost:8000/api/v1/products/parse" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://kaspi.kz/shop/p/product-id/"}'
```

### Получение данных
```bash
# Список всех товаров
curl "http://localhost:8000/api/v1/products/"

# Конкретный товар
curl "http://localhost:8000/api/v1/products/{id}"
```

### Структура базы данных

**Основные таблицы:**
- `products` - основная информация о товарах
- `product_offers` - офферы продавцов
- `product_attributes` - характеристики товаров
- `product_images` - изображения товаров
- `product_price_history` - история изменения цен
- `product_offers_history` - история изменения офферов

## Скриншоты работы

### API документация (Swagger UI)
![API Docs](screens/image.png)

### Результат парсинга товара
![Product Parsing](screens/image1.png)

### Список товаров в базе
![Products List](screens/image3.png)

### Структура данных товара
![Product Data](screens/image4.png)

### Офферы продавцов
![Offers Data](screens/image5.png)

### Логи системы в JSON формате
![Logs](screens/image6.png)

## 🔧 Конфигурация

### Переменные окружения (.env)
```env
# База данных
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db
DB_PORT=5432

# Приложение
APP_NAME=Kaspi Parser
DEBUG=True
LOG_LEVEL=INFO

# Парсинг
PARSER_DELAY=2
MAX_RETRIES=3
```

### Логирование
- **Формат**: JSON с полями timestamp, level, source, message
- **Ротация**: файлы до 5MB, хранение до 5 файлов
- **Расположение**: `logs/logs/app.log`

## Что реализовано из ТЗ

### ✅ Обязательные требования
- [x] Выбор товара и фиксация URL в `seed.json`
- [x] Сбор основной информации (название, категория, цены, рейтинг, отзывы)
- [x] Сохранение в PostgreSQL
- [x] Экспорт в JSON (`export/products/`)
- [x] Настроенное хранилище PostgreSQL

### ✅ Дополнительные возможности
- [x] Характеристики товара (key-value)
- [x] Офферы продавцов в `export/offers/`
- [x] Ссылки на изображения
- [x] Количество продавцов
- [x] Логирование в JSON формате
- [x] Docker + Docker Compose
- [x] Alembic миграции
- [x] Полная типизация с Pydantic
- [x] RESTful API с документацией


**Дата создания**: 07.10.2025  
