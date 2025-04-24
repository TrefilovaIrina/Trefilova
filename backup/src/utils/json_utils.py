import json
import re
from typing import Dict, Any, Union
from ..exceptions.prompt_exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Компилируем регулярное выражение для удаления markdown-разметки
MARKDOWN_JSON_PATTERN = re.compile(r'```json\s*|\s*```')

def clean_json_text(text: str) -> str:
    """Очистка текста от markdown-разметки."""
    return MARKDOWN_JSON_PATTERN.sub('', text).strip()

def parse_json_result(text: str) -> dict:
    """Парсит JSON из текста ответа."""
    try:
        # Находим начало и конец JSON в тексте
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start == -1 or end == 0:
            raise ValueError("JSON не найден в тексте")
            
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Ошибка при парсинге JSON: {str(e)}")
        return {}

def safe_json_loads(text: Union[str, bytes, bytearray]) -> Dict[str, Any]:
    """Безопасная загрузка JSON с обработкой ошибок."""
    try:
        if isinstance(text, (bytes, bytearray)):
            text = text.decode('utf-8')
        return json.loads(clean_json_text(text))
    except json.JSONDecodeError as e:
        raise ValidationError(f"Ошибка декодирования JSON: {str(e)}\nТекст: {text}")
    except Exception as e:
        raise ValidationError(f"Неожиданная ошибка при обработке JSON: {str(e)}") 