import logging
import os
from typing import Optional

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Настраивает и возвращает логгер с заданной конфигурацией."""
    # Создаем директорию для логов, если она не существует
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Получаем или создаем логгер
    logger = logging.getLogger(name if name else __name__)
    
    # Если обработчики уже добавлены, возвращаем существующий логгер
    if logger.handlers:
        return logger
    
    # Устанавливаем уровень логирования
    logger.setLevel(logging.INFO)
    
    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Добавляем обработчик для записи в файл
    file_handler = logging.FileHandler(
        os.path.join(log_dir, "app.log"),
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Добавляем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger 