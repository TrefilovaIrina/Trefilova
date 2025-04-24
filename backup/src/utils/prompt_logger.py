import json
from datetime import datetime
from src.utils.db_utils import init_db, log_prompt, get_logs, clear_logs

class PromptLogger:
    """Класс для логирования промптов в базу данных"""
    
    def __init__(self):
        """Инициализация логгера"""
        self.session = init_db()
    
    def log_prompt(self, original_prompt: str, enhanced_prompt: str, metadata: dict = None):
        """Сохранение промпта в базу данных"""
        log_prompt(self.session, original_prompt, enhanced_prompt, metadata)
    
    def get_logs(self, limit: int = None):
        """Получение логов из базы данных"""
        logs = get_logs(self.session, limit)
        return [
            {
                "timestamp": log.timestamp.isoformat(),
                "original_prompt": log.original_prompt,
                "enhanced_prompt": log.enhanced_prompt,
                "metadata": log.prompt_metadata
            }
            for log in logs
        ]
    
    def clear_logs(self):
        """Очистка всех логов"""
        clear_logs(self.session)
        return True 