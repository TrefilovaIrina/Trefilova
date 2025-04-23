import streamlit as st
import os
from dotenv import load_dotenv
from src.services.prompt_processor import PromptProcessor
from src.components import (
    display_prompt_enhancement,
    display_prompt_navigator,
    display_useful_tips
)
import logging
from src.config import (
    get_openai_api_key,
    OPENAI_MODEL,
    setup_page,
    load_css,
    logger
)

def main():
    """Основная функция приложения"""
    try:
        # Загрузка переменных окружения
        load_dotenv()
        logger.info("Переменные окружения загружены")
        
        # Получение API ключа
        api_key = get_openai_api_key()
        if not api_key:
            st.error("Ошибка: Не найден API ключ OpenAI. Пожалуйста, добавьте его в файл .env")
            st.info("Для работы приложения необходим API ключ OpenAI. Добавьте его в файл .env в формате: OPENAI_API_KEY=your_key_here")
            return
            
        # Инициализация обработчика промптов
        try:
            prompt_processor = PromptProcessor(
                api_key=api_key,
                model_name=OPENAI_MODEL
            )
            # Сохраняем API ключ в состоянии сессии
            st.session_state['openai_api_key'] = api_key
            logger.info("PromptProcessor успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации PromptProcessor: {str(e)}")
            st.error("Ошибка при инициализации обработчика промптов. Пожалуйста, проверьте настройки.")
            st.info(f"Детали ошибки: {str(e)}")
            return
        
        # Настройка страницы
        setup_page()
        load_css()
        
        # Заголовок приложения
        st.title("✨ Prompt Enhancer")
        
        # Навигация
        st.sidebar.title("Навигация")
        page = st.sidebar.radio(
            "Выберите инструмент:",
            ["Улучшение промпта", "Навигатор промптов", "Полезные советы"]
        )
        
        # Отображение выбранной страницы
        if page == "Улучшение промпта":
            display_prompt_enhancement(prompt_processor)
        elif page == "Навигатор промптов":
            display_prompt_navigator(prompt_processor)
        elif page == "Полезные советы":
            display_useful_tips()
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке страницы: {str(e)}")
        st.error("Произошла ошибка при загрузке приложения. Пожалуйста, попробуйте обновить страницу.")
        st.info(f"Детали ошибки: {str(e)}")

if __name__ == "__main__":
    main() 