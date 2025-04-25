import os
import pytest
from langchain_community.chat_models import ChatOpenAI
from unittest.mock import patch

def test_chatopenai_initialization():
    """Тест инициализации ChatOpenAI."""
    api_key = "test-api-key"
    
    # Тест 1: Базовая инициализация
    try:
        llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        assert llm is not None
        print("✅ Базовая инициализация успешна")
    except Exception as e:
        print(f"❌ Ошибка при базовой инициализации: {str(e)}")
        raise

    # Тест 2: Проверка всех возможных параметров
    try:
        llm = ChatOpenAI(
            api_key=api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000,
            request_timeout=30,
            streaming=False
        )
        assert llm is not None
        print("✅ Расширенная инициализация успешна")
    except Exception as e:
        print(f"❌ Ошибка при расширенной инициализации: {str(e)}")
        raise

    # Тест 3: Проверка с переменными окружения
    with patch.dict(os.environ, {'OPENAI_API_KEY': api_key}):
        try:
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7
            )
            assert llm is not None
            print("✅ Инициализация с переменными окружения успешна")
        except Exception as e:
            print(f"❌ Ошибка при инициализации с переменными окружения: {str(e)}")
            raise

def test_chatopenai_client_attributes():
    """Тест для проверки атрибутов клиента после инициализации."""
    api_key = "test-api-key"
    
    llm = ChatOpenAI(
        api_key=api_key,
        model_name="gpt-3.5-turbo",
        temperature=0.7
    )
    
    # Проверяем, что клиент имеет правильные атрибуты
    assert hasattr(llm, 'client'), "У ChatOpenAI должен быть атрибут client"
    assert hasattr(llm, 'model_name'), "У ChatOpenAI должен быть атрибут model_name"
    assert hasattr(llm, 'temperature'), "У ChatOpenAI должен быть атрибут temperature"
    
    # Проверяем значения атрибутов
    assert llm.model_name == "gpt-3.5-turbo"
    assert llm.temperature == 0.7
    
    print("✅ Все атрибуты клиента проверены успешно")

if __name__ == "__main__":
    print("Запуск тестов инициализации ChatOpenAI...")
    test_chatopenai_initialization()
    test_chatopenai_client_attributes()
    print("Все тесты завершены!") 