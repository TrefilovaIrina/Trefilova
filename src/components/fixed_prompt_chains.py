from src.utils.clipboard import copy_to_clipboard_js

def copy_to_clipboard(text: str) -> bool:
    """Копирует текст в буфер обмена с использованием JavaScript."""
    try:
        copy_to_clipboard_js(text)
        return True
    except Exception as e:
        logger.error(f"Ошибка при копировании в буфер обмена: {str(e)}")
        return False 