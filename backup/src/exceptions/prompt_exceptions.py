class PromptProcessorError(Exception):
    """Базовый класс для ошибок обработки промптов."""
    pass

class APIError(PromptProcessorError):
    """Ошибка при работе с API."""
    pass

class CacheError(PromptProcessorError):
    """Ошибка при работе с кэшем."""
    pass

class ValidationError(PromptProcessorError):
    """Ошибка валидации данных."""
    pass 