from typing import List, Dict, Any, Optional
import logging
from src.models.idea_models import CreativeApproach
from src.chains.idea_chains import IdeaChains
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from src.models.creative_approaches import CREATIVE_APPROACHES
from src.config import OPENAI_MAX_TOKENS, OPENAI_MODEL, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)

class IdeaProcessor:
    """Сервис для работы с креативными подходами"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Инициализация процессора идей"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API ключ OpenAI не найден. Укажите его через параметр api_key или переменную окружения OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(
            model_name=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            openai_api_key=self.api_key,
            max_tokens=OPENAI_MAX_TOKENS,
            request_timeout=30,
            max_retries=3
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("IdeaProcessor успешно инициализирован")
        self.idea_chains = IdeaChains(api_key=self.api_key)
        self.approaches = self._load_approaches()
    
    def _load_approaches(self) -> List[CreativeApproach]:
        """Загружает список доступных подходов"""
        return list(CREATIVE_APPROACHES.values())
    
    def analyze_idea(self, idea: str, context: str = "") -> Dict[str, Any]:
        """Анализирует идею и возвращает структурированный результат"""
        logger.info("Начало анализа идеи")
        
        # Подготовка входных данных
        input_data = {
            "idea": idea,
            "context": context,
            "approaches": [approach.name for approach in self.approaches]
        }
        
        # Создание промпта
        prompt = PromptTemplate(
            input_variables=["idea", "context", "approaches"],
            template="""
            Проанализируйте следующую идею и выберите наиболее подходящий подход из списка.
        
        Идея: {idea}
            Контекст: {context}
            Доступные подходы: {approaches}
            
            Выберите один подход и объясните, почему он наиболее подходит для данной идеи.
            
            ВАЖНО: Верните только JSON-объект в следующем формате:
            {{"selected_approach": "название_подхода", "explanation": "объяснение_выбора"}}
            
            Выберите один из следующих подходов: {approaches}
            """
        )
        
        try:
            # Создание и выполнение цепочки
            chain = (
                {"idea": RunnablePassthrough(), 
                 "context": lambda x: context, 
                 "approaches": lambda x: [a.name for a in self.approaches]} 
                | prompt 
                | self.llm
            )
            
            # Получаем ответ
            response = chain.invoke(idea)
            response_text = response.content.strip()
            
            # Разбираем JSON
            result = json.loads(response_text)
            
            # Проверяем наличие необходимых полей
            required_fields = ['selected_approach', 'explanation']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                logger.warning(f"В ответе отсутствуют обязательные поля: {missing_fields}")
                return {
                    'selected_approach': self.approaches[0].name,
                    'explanation': "Не удалось проанализировать идею. Используется подход по умолчанию.",
                    'template': self.approaches[0].prompt_template
                }
            
            # Получение шаблона для выбранного подхода
            selected_approach = next(
                (approach for approach in self.approaches if approach.name == result['selected_approach']),
                self.approaches[0]
            )
            
            result['template'] = selected_approach.prompt_template
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при анализе идеи: {str(e)}")
            raise
    
    def process_idea(self, idea: str, context: str = "") -> Dict[str, Any]:
        """Обрабатывает идею и выбирает подходящий подход"""
        try:
            # Анализируем идею
            analysis_result = self.analyze_idea(idea, context)
            
            # Получаем выбранный подход
            selected_approach = next(
                (approach for approach in self.approaches if approach.name == analysis_result['selected_approach']),
                self.approaches[0]
            )
            
            # Подставляем значение идеи в шаблон
            try:
                # Пробуем сначала с {idea}
                template = selected_approach.prompt_template.format(idea=idea)
            except KeyError:
                try:
                    # Если не получилось, пробуем с {Ключевая идея}
                    template = selected_approach.prompt_template.format(**{"Ключевая идея": idea})
                except KeyError:
                    # Если и это не получилось, используем шаблон как есть
                    template = selected_approach.prompt_template
            
            # Генерируем идеи на основе шаблона
            generated_ideas = [template]  # Пока возвращаем только шаблон как идею
            
            return {
                'selected_approach': selected_approach.name,
                'explanation': analysis_result['explanation'],
                'template': template,
                'generated_ideas': generated_ideas
            }
            
        except Exception as e:
            logger.error(f"Ошибка при обработке идеи: {str(e)}")
            raise 