import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PromptLogger:
    """Класс для логирования промптов."""
    
    def __init__(self, log_file: str = "prompt_logs.json"):
        """Инициализация логгера промптов."""
        self.log_file = log_file
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self):
        """Проверяет существование файла логов и создает его при необходимости."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log_prompt(self, original_prompt: str, enhanced_prompt: str, metadata: dict = None):
        """Сохраняет информацию о промпте в лог."""
        try:
            # Загружаем существующие логи
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Создаем новую запись
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "original_prompt": original_prompt,
                "enhanced_prompt": enhanced_prompt,
                "metadata": metadata or {}
            }
            
            # Добавляем новую запись
            logs.append(log_entry)
            
            # Сохраняем обновленные логи
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Промпт успешно залогирован: {len(logs)} записей в логе")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при логировании промпта: {str(e)}")
            return False
    
    def get_logs(self, limit: int = None):
        """Получает последние логи промптов."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if limit:
                logs = logs[-limit:]
            
            return logs
            
        except Exception as e:
            logger.error(f"Ошибка при чтении логов: {str(e)}")
            return []
    
    def clear_logs(self):
        """Очищает все логи."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            logger.info("Логи успешно очищены")
            return True
        except Exception as e:
            logger.error(f"Ошибка при очистке логов: {str(e)}")
            return False 