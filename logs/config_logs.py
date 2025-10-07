import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import os

# создаём директорию для логов, если нет
os.makedirs("logs/logs", exist_ok=True)

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # проверяем, чтобы не добавлять второй handler
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        handler = RotatingFileHandler(
            "logs/logs/app.log",     # правильный путь в logs/logs
            maxBytes=5_000_000,      # ~5MB
            backupCount=5,           # храним до 5 файлов
            encoding="utf-8"
        )

        # JSON formatter для файла с поддержкой Unicode
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level", 
                "name": "source",
                "message": "msg"
            },
            json_ensure_ascii=False  # Позволяет использовать Unicode символы
        )

        handler.setFormatter(json_formatter)
        root_logger.addHandler(handler)
        
        # Добавляем консольный handler для отладки (обычный текстовый формат)
        if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # убираем лишние логи от httpx/httpcore
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        
        print("Logging setup complete. Log file: logs/logs/app.log")
