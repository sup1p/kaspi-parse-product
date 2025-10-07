# Используем единый образ для упрощения
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Настройки uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV PYTHONUNBUFFERED=1

# Устанавливаем все системные зависимости сразу (для кеширования)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Базовые инструменты
    bash wget ca-certificates gnupg curl \
    # Зависимости для компиляции Python пакетов
    build-essential \
    # Все зависимости Playwright/Chromium
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxss1 libasound2 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libpango-1.0-0 libxcb1 libxshmfence1 libdrm2 \
    libxfixes3 libxext6 libxi6 libxrender1 libxtst6 libgl1-mesa-glx \
    fonts-liberation libpci3 libxkbcommon0 xvfb \
 && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей (кешируется при изменениях только этих файлов)
COPY pyproject.toml uv.lock ./

# Устанавливаем Python зависимости (кешируется)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Копируем код приложения (в конце для лучшего кеширования)
COPY . .

# Устанавливаем сам проект
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Устанавливаем браузеры Playwright ПОСЛЕ установки проекта
RUN /app/.venv/bin/python -m playwright install --with-deps chromium

# Создаём папки для логов
RUN mkdir -p /app/logs/logs && touch /app/logs/logs/app.log

# Исправляем права доступа и формат entrypoint.sh
RUN chmod +x /app/entrypoint.sh && \
    # Конвертируем CRLF в LF на случай Windows
    sed -i 's/\r$//' /app/entrypoint.sh

# Устанавливаем переменные окружения
ENV PATH="/app/.venv/bin:$PATH"
ENV APP_ENV=production

# Порт приложения
EXPOSE 8000

# Запуск приложения
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
