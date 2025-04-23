import pytest
from unittest.mock import Mock, patch
from src.components.navigator.navigator import PromptNavigator
import os
import json

@pytest.fixture
def navigator():
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        return PromptNavigator()

def test_generate_clarifying_questions(navigator):
    # Подготовка тестовых данных
    task = "Написать промпт для генерации текста"
    expected_questions = [
        "Какова основная цель задачи?",
        "В каком формате нужен результат?",
        "Какие ограничения нужно учесть?"
    ]
    
    # Настройка мока
    with patch('langchain_openai.ChatOpenAI.invoke') as mock_invoke:
        mock_response = Mock()
        mock_response.content = "1. Какова основная цель задачи?\n2. В каком формате нужен результат?\n3. Какие ограничения нужно учесть?"
        mock_invoke.return_value = mock_response
        
        # Выполнение теста
        questions = navigator.generate_clarifying_questions(task)
        
        # Проверки
        assert len(questions) == len(expected_questions)
        assert all(q in questions for q in expected_questions)
        mock_invoke.assert_called_once()

def test_analyze_task(navigator):
    # Подготовка тестовых данных
    task = "Написать промпт"
    answers = {
        "Какова цель?": "Генерация текста",
        "Какой формат?": "JSON"
    }
    expected_analysis = {
        "task_type": "text generation",
        "approach": "пошаговый анализ",
        "steps": [
            {
                "step_number": 1,
                "description": "Анализ требований",
                "llm": "GPT-3.5-turbo",
                "step_prompt": "Проанализируй требования"
            }
        ]
    }
    
    # Настройка мока
    with patch('langchain_openai.ChatOpenAI.invoke') as mock_invoke:
        mock_response = Mock()
        mock_response.content = json.dumps(expected_analysis)
        mock_invoke.return_value = mock_response
        
        # Выполнение теста
        analysis = navigator.analyze_task(task, answers)
        
        # Проверки
        assert analysis == expected_analysis
        mock_invoke.assert_called_once()

def test_generate_prompt(navigator):
    # Подготовка тестовых данных
    task = "Написать промпт"
    analysis = {
        "task_type": "text generation",
        "approach": "пошаговый анализ",
        "steps": [
            {
                "step_number": 1,
                "description": "Анализ требований",
                "llm": "GPT-3.5-turbo",
                "step_prompt": "Проанализируй требования"
            }
        ]
    }
    expected_prompt = "Ты - эксперт по генерации текста. Твоя задача..."
    
    # Настройка мока
    with patch('langchain_openai.ChatOpenAI.invoke') as mock_invoke:
        mock_response = Mock()
        mock_response.content = expected_prompt
        mock_invoke.return_value = mock_response
        
        # Выполнение теста
        prompt = navigator.generate_prompt(task, analysis)
        
        # Проверки
        assert prompt == expected_prompt
        mock_invoke.assert_called_once() 