import pytest
from unittest.mock import Mock, patch
from src.components.navigator.navigator import PromptNavigator
import os
import json

@pytest.fixture
def navigator():
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        return PromptNavigator(api_key='test-key')

def test_generate_clarifying_questions(navigator):
    """Тест генерации уточняющих вопросов."""
    task = "Написать статью о искусственном интеллекте"
    
    # Настройка мока
    with patch('langchain_openai.ChatOpenAI.invoke') as mock_invoke:
        mock_response = Mock()
        mock_response.content = "1. Какова цель статьи?\n2. Какой объем текста требуется?\n3. Какой стиль изложения предпочтителен?"
        mock_invoke.return_value = mock_response
        
        # Выполнение теста
        questions = navigator.generate_clarifying_questions(task)
        
        # Проверки
        assert isinstance(questions, list)
        assert len(questions) > 0
        assert all(isinstance(q, str) for q in questions)
        assert all(q.endswith('?') for q in questions)
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
                "description": "Анализ требований для создания эффективного промпта. Этот шаг включает в себя изучение целей, ограничений и специфических требований к выходным данным.",
                "llm": "GPT-3.5-turbo - оптимальный выбор для анализа требований, благодаря высокой точности и способности понимать контекст задачи",
                "step_prompt": "Проанализируй следующие требования и определи ключевые элементы для создания эффективного промпта: цели, ограничения, формат вывода и специфические требования."
            },
            {
                "step_number": 2,
                "description": "Структурирование промпта с учетом всех требований и лучших практик. Включает создание четкой структуры с инструкциями, примерами и критериями качества.",
                "llm": "GPT-3.5-turbo - идеальный выбор для структурирования промпта, так как модель хорошо понимает принципы создания эффективных инструкций",
                "step_prompt": "На основе проведенного анализа создай структурированный промпт, который включает четкие инструкции, релевантные примеры и критерии оценки качества результата."
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
        assert analysis is not None
        assert analysis["task_type"] == expected_analysis["task_type"]
        assert analysis["approach"] == expected_analysis["approach"]
        assert len(analysis["steps"]) == len(expected_analysis["steps"])
        for actual_step, expected_step in zip(analysis["steps"], expected_analysis["steps"]):
            assert actual_step["step_number"] == expected_step["step_number"]
            assert actual_step["description"] == expected_step["description"]
            assert actual_step["llm"] == expected_step["llm"]
            assert actual_step["step_prompt"] == expected_step["step_prompt"]
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
                "llm": "GPT-3.5-turbo - оптимальный выбор для анализа требований, благодаря высокой точности и способности понимать контекст задачи",
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