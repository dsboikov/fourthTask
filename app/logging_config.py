import logging
import sys

def setup_logging():
    """Настраиваем логирование для всего приложения"""
    # Создаём форматтер
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Обработчик для stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Убираем дублирование
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True