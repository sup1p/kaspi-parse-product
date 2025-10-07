import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import os

# создаём директорию для логов, если нет
os.makedirs("logs", exist_ok=True)

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # проверяем, чтобы не добавлять второй handler
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        handler = RotatingFileHandler(
            "logs/app.log",          # исправлено на логичный путь
            maxBytes=5_000_000,      # ~5MB
            backupCount=5,           # храним до 5 файлов
            encoding="utf-8"
        )

        # JSON formatter
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "source",
                "message": "msg"
            }
        )

        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

        # убираем лишние логи от httpx/httpcore
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
