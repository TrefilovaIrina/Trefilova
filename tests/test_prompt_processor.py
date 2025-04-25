import os
import pytest
from unittest.mock import patch, MagicMock
from src.services.prompt_processor import PromptProcessor
from src.exceptions.prompt_exceptions import APIError

def test_prompt_processor_initialization():
    """Тест инициализации PromptProcessor."""
    api_key = "test-api-key"
    
    # Тест 1: Базовая инициализация
    try:
        processor = PromptProcessor(
            api_key=api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        assert processor is not None
        assert processor.llm is not None
        print("✅ Базовая инициализация PromptProcessor успешна")
    except Exception as e:
        print(f"❌ Ошибка при базовой инициализации PromptProcessor: {str(e)}")
        raise

    # Тест 2: Инициализация с переменными окружения
    with patch.dict(os.environ, {'OPENAI_API_KEY': api_key}):
        try:
            processor = PromptProcessor()
            assert processor is not None
            assert processor.llm is not None
            print("✅ Инициализация PromptProcessor с переменными окружения успешна")
        except Exception as e:
            print(f"❌ Ошибка при инициализации PromptProcessor с переменными окружения: {str(e)}")
            raise

def test_prompt_processor_chain_initialization():
    """Тест инициализации цепочек в PromptProcessor."""
    api_key = "test-api-key"
    
    try:
        processor = PromptProcessor(
            api_key=api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Проверяем инициализацию цепочек
        assert processor.analysis_chain is not None
        assert processor.enhancement_chain is not None
        print("✅ Инициализация цепочек в PromptProcessor успешна")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации цепочек: {str(e)}")
        raise

def test_prompt_processor_error_handling():
    """Тест обработки ошибок в PromptProcessor."""
    
    # Тест 1: Отсутствие API ключа
    with patch.dict(os.environ, {}, clear=True):  # Очищаем все переменные окружения
        with pytest.raises(APIError, match="OPENAI_API_KEY не установлен в переменных окружения"):
            processor = PromptProcessor(api_key=None)
    
    # Тест 2: Неверный API ключ
    try:
        processor = PromptProcessor(api_key="invalid-key")
        assert processor is not None
        print("✅ Инициализация с неверным API ключом прошла успешно (валидация ключа происходит позже)")
    except Exception as e:
        print(f"❌ Неожиданная ошибка при инициализации с неверным API ключом: {str(e)}")
        raise

if __name__ == "__main__":
    print("Запуск тестов PromptProcessor...")
    test_prompt_processor_initialization()
    test_prompt_processor_chain_initialization()
    test_prompt_processor_error_handling()
    print("Все тесты завершены!") 