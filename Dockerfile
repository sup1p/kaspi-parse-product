# ---- builder: устанавливаем зависимости и формируем .venv ----
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

# Настройки uv (сохраняем как у тебя)
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Копируем только манифесты зависимостей для кэшируемой установки
COPY pyproject.toml uv.lock /app/

# Устанавливаем системные зависимости, нужные для установки Python-пакетов и Playwright
# (убираем кэш apt в конце)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates gnupg \
    build-essential curl zip unzip \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxss1 libasound2 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libpango-1.0-0 libxcb1 libxshmfence1 libdrm2 \
    fonts-liberation libpci3 libxkbcommon0 \
 && rm -rf /var/lib/apt/lists/*

# Сборка зависимостей проекта в .venv (uv создаст .venv в /app/.venv)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Копируем весь проект после создания .venv
COPY . /app

# Устанавливаем проект зависимости в .venv (локальный пакет)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Устанавливаем Playwright-браузеры внутри .venv
# Убедись, что в pyproject.toml у тебя есть dependency: playwright
# Команда ниже запускает установщик браузеров (Chromium) и дополнительные зависимости
RUN /app/.venv/bin/python -m playwright install --with-deps chromium

# ---- runtime: минимальный образ с готовой виртуальной средой ----
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS runtime

WORKDIR /app

# Устанавливаем системные зависимости для Playwright в runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxss1 libasound2 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libpango-1.0-0 libxcb1 libxshmfence1 libdrm2 \
    fonts-liberation libpci3 libxkbcommon0 ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Копируем готовый проект/venv из билдера
COPY --from=builder /app /app
# Копируем установленные браузеры Playwright
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Создаём папку под логи (как у тебя)
RUN mkdir -p /app/logs/logs && [ -f /app/logs/logs/logs.log ] || touch /app/logs/logs/logs.log

# Устанавливаем переменные окружения
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# Порт приложения
EXPOSE 8000

# Запуск uvicorn через uv (как у тебя)
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
