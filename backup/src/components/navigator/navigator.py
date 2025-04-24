from typing import Dict, List, Optional, Any
import logging
import streamlit as st
import os
import json
from langchain_openai import ChatOpenAI
from src.config import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)

class PromptNavigator:
    """Класс для управления процессом навигации по созданию промпта."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Инициализация навигатора промптов."""
        try:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY не установлен в переменных окружения")
            
            self.llm = ChatOpenAI(
                api_key=api_key,
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
                request_timeout=30,
                max_retries=3
            )
            logger.info("PromptNavigator успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации PromptNavigator: {str(e)}")
            raise

    def generate_clarifying_questions(self, task: str) -> List[str]:
        """Генерация уточняющих вопросов для задачи."""
        try:
            if not task or not task.strip():
                logger.error("Получена пустая задача")
                return []

            prompt = f"""
            Ты — эксперт по формулировке задач для нейросетей. Твоя задача — сгенерировать уточняющие вопросы для решения следующей задачи при помощи нейросети:

            ЗАДАЧА:
            "{task}"

            ИНСТРУКЦИИ:
            1. Сгенерируй от 3 до 7 уточняющих вопросов
            2. Каждый вопрос должен быть на новой строке
            3. Каждый вопрос должен начинаться с номера и точки (например, "1. Вопрос?")
            4. Вопросы должны быть конкретными и направленными на уточнение пользовательской задачи:
               - цели пользователя
               - формата результата
               - типа данных
               - ограничений
               - критериев успеха
               - языка и стиля
               - уровня детализации
               - специфических требований

            ФОРМАТ ОТВЕТА:
            1. Первый вопрос?
            2. Второй вопрос?
            3. Третий вопрос?

            ВАЖНО: 
            - Выведи ТОЛЬКО список вопросов
            - Не добавляй никаких дополнительных пояснений
            - Каждый вопрос должен заканчиваться знаком вопроса
            - Не используй никаких дополнительных символов или форматирования
            """
            
            logger.info(f"Отправка запроса к LLM для задачи: {task[:100]}...")
            
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            if not response_text or not response_text.strip():
                logger.error("Получен пустой ответ от LLM")
                return []
            
            questions = []
            for line in response_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Проверяем, что строка начинается с цифры и точки
                if line[0].isdigit() and '. ' in line:
                    question = line.split('. ', 1)[1].strip()
                    if question and len(question) > 5 and question.endswith('?'):
                        questions.append(question)
            
            if not questions:
                logger.warning("Не удалось извлечь вопросы из ответа LLM")
                logger.debug(f"Исходный ответ: {response_text}")
                return []
            
            logger.info(f"Успешно извлечено {len(questions)} вопросов")
            return questions
            
        except Exception as e:
            logger.error(f"Ошибка при генерации вопросов: {str(e)}")
            return []

    def analyze_task(self, task: str, answers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Анализ задачи на основе ответов на уточняющие вопросы."""
        try:
            prompt = f"""
            Ты — архитектор AI‑решений и эксперт по промт инжинирингу.
            На основе следующей задачи и ответов на уточняющие вопросы сгенерируй пошаговое решение задачи.

            ЗАДАЧА:
            {task}

            ВОПРОСЫ И ОТВЕТЫ:
            {json.dumps(answers, ensure_ascii=False, indent=2)}

            ТВОЯ ЗАДАЧА:
            1. Определи тип задачи («task_type»).
            2. Предложи общий подход («approach»).
            3. Разбей решение на последовательные шаги («steps»). Для каждого:
                • «step_number» — порядковый номер (целое число, начиная с 1);  
                • «description» — подробное описание что делаем на этом шаге;  
                • «llm» — какая LLM оптимальна (GPT‑4, Claude 3, Perplexity и т.д.) с коротким пояснением выбора;  
                • «step_prompt» — детальный промпт для выполнения этого шага.

            ВАЖНО: 
            1. Ответ должен быть строго в формате JSON
            2. Не добавляй никаких пояснений или текста до или после JSON
            3. Используй только двойные кавычки для строк
            4. Все поля должны содержать непустые значения
            5. Описания и промпты должны быть подробными, не менее 50 символов
            6. Поле step_number должно быть целым числом без кавычек (не строкой)
            7. Должно быть минимум 2 шага в решении

            ПРИМЕР ПРАВИЛЬНОГО ОТВЕТА:
            {{
                "task_type": "text generation",
                "approach": "Разобьем задачу на этапы анализа и генерации, используя специализированные модели для каждого шага",
                "steps": [
                    {{
                        "step_number": 1,
                        "description": "Анализ исходного текста для определения ключевых тем, стиля и структуры. Это поможет сохранить согласованность в генерируемом контенте.",
                        "llm": "Claude 3 Sonnet - отлично подходит для глубокого анализа текста благодаря большому контексту и пониманию нюансов",
                        "step_prompt": "Проанализируй следующий текст и определи: 1) основные темы и подтемы, 2) стиль изложения и тон, 3) структуру и форматирование, 4) ключевые термины и концепции. Представь результат в структурированном виде."
                    }},
                    {{
                        "step_number": 2,
                        "description": "Генерация нового текста на основе результатов анализа, с сохранением выявленного стиля и структуры",
                        "llm": "GPT-4 - лучший выбор для творческой генерации с сохранением согласованности и качества",
                        "step_prompt": "На основе предоставленного анализа сгенерируй новый текст. Сохрани: 1) выявленный стиль и тон, 2) структуру и форматирование, 3) использование ключевых терминов. Текст должен быть логически связным и соответствовать исходному контексту."
                    }}
                ]
            }}

            ОБРАТИ ВНИМАНИЕ:
            - В примере step_number это число без кавычек: 1, 2 (НЕ "1", "2")
            - Все описания подробные и информативные
            - Нет пустых или отсутствующих полей
            - Используются только двойные кавычки
            - JSON должен быть валидным
            """
            
            logger.info("Отправка запроса на анализ задачи")
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Очищаем ответ от возможных лишних символов и пробелов
            response_text = response_text.strip()
            
            # Логируем полученный ответ для отладки
            logger.debug(f"Полученный ответ от LLM: {response_text}")
            
            # Ищем JSON в ответе
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start == -1 or json_end == -1:
                logger.error("В ответе не найден JSON объект")
                logger.debug(f"Полученный ответ: {response_text}")
                return None
                
            # Извлекаем только JSON часть
            json_text = response_text[json_start:json_end + 1]
            
            try:
                # Пытаемся сначала очистить возможные проблемы с форматированием
                json_text = json_text.replace("'", '"')  # Заменяем одинарные кавычки на двойные
                json_text = json_text.replace('\n', ' ')  # Убираем переносы строк
                json_text = json_text.replace('\r', ' ')  # Убираем возвраты каретки
                
                # Пытаемся исправить проблему с числовыми значениями в строках
                import re
                # Ищем паттерны вида "step_number": "1" или "step_number":"1"
                json_text = re.sub(r'"step_number"\s*:\s*"(\d+)"', r'"step_number": \1', json_text)
                # Также ищем паттерны с одинарными кавычками
                json_text = re.sub(r"'step_number'\s*:\s*'(\d+)'", r'"step_number": \1', json_text)
                
                # Пытаемся загрузить JSON
                try:
                    result = json.loads(json_text)
                except json.JSONDecodeError as e:
                    # Если не получилось, пробуем более агрессивную очистку
                    json_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_text)  # Убираем управляющие символы
                    json_text = re.sub(r'\s+', ' ', json_text)  # Нормализуем пробелы
                    result = json.loads(json_text)
                
                # Проверяем наличие обязательных полей
                required_fields = ['task_type', 'approach', 'steps']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    logger.error(f"В ответе отсутствуют обязательные поля: {', '.join(missing_fields)}")
                    logger.debug(f"Полученный результат: {result}")
                    return None

                # Проверяем, что значения не пустые
                if not result['task_type'] or not result['approach']:
                    logger.error("Поля task_type и approach не могут быть пустыми")
                    return None
                
                # Проверяем структуру steps
                if not isinstance(result['steps'], list) or len(result['steps']) < 2:
                    logger.error("Поле 'steps' должно быть списком с минимум 2 шагами")
                    return None
                    
                # Проверяем каждый шаг
                for i, step in enumerate(result['steps']):
                    step_fields = ['step_number', 'description', 'llm', 'step_prompt']
                    
                    # Проверяем наличие всех полей
                    missing_step_fields = [field for field in step_fields if field not in step]
                    if missing_step_fields:
                        logger.error(f"В шаге {i+1} отсутствуют обязательные поля: {', '.join(missing_step_fields)}")
                        return None
                    
                    # Конвертируем step_number в число, если это строка или float
                    try:
                        if isinstance(step['step_number'], str):
                            step['step_number'] = int(float(step['step_number']))
                        elif isinstance(step['step_number'], float):
                            step['step_number'] = int(step['step_number'])
                    except (ValueError, TypeError):
                        logger.error(f"В шаге {i+1} поле 'step_number' должно быть числом")
                        return None
                    
                    # Проверяем типы данных и непустые значения
                    if not isinstance(step['step_number'], int) or step['step_number'] < 1:
                        logger.error(f"В шаге {i+1} поле 'step_number' должно быть положительным целым числом")
                        return None
                        
                    for field in ['description', 'llm', 'step_prompt']:
                        if not isinstance(step[field], str) or len(step[field].strip()) < 50:
                            logger.error(f"В шаге {i+1} поле '{field}' должно быть непустой строкой длиной не менее 50 символов")
                            return None
                
                logger.info("Анализ задачи успешно завершен")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка при парсинге JSON: {str(e)}")
                logger.debug(f"Полученный ответ: {response_text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при анализе задачи: {str(e)}")
            return None

    def generate_prompt(self, task: str, analysis: Dict[str, Any]) -> Optional[str]:
        """Генерация финального промпта на основе анализа задачи."""
        try:
            prompt = f"""
            Ты — эксперт по промт-инжинирингу. На основе следующей задачи и анализа создай финальный промпт:

            ЗАДАЧА:
            {task}

            АНАЛИЗ ЗАДАЧИ:
            {json.dumps(analysis, ensure_ascii=False, indent=2)}

            Создай финальный промпт, который:
            1. Четко описывает задачу и ожидаемый результат
            2. Включает все необходимые параметры и ограничения
            3. Содержит инструкции по форматированию ответа
            4. Просит решение ПОШАГОВО с обоснованием
            5. Самодостаточен — не требует уточнений
            6. Указывает на необходимость пошагового решения
            7. Требует обоснования каждого шага
            8. Включает проверку качества результата

            ВАЖНО: Промпт должен быть самодостаточным и не требовать дополнительных уточнений.
            """
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Ошибка при генерации промпта: {str(e)}")
            return None 