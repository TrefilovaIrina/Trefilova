import os
import time
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

from ..models.prompt_models import PromptAnalysis, EnhancementResult
from ..exceptions.prompt_exceptions import PromptProcessorError, APIError
from ..utils.json_utils import parse_json_result
from ..chains.fixed_prompt_chains import PromptChains
from ..config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS

logger = logging.getLogger(__name__)

class PromptProcessor:
    """
    Процессор для анализа и улучшения промптов.
    
    Основные функции:
    1. Анализ промпта и выявление недостающих элементов
    2. Обработка данных из сайдбара
    3. Анализ референсного текста
    4. Генерация улучшенного промпта
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = OPENAI_MODEL, temperature: float = OPENAI_TEMPERATURE):
        """Initialize the prompt processor."""
        try:
            if not api_key:
                raise APIError("OPENAI_API_KEY не установлен в переменных окружения")
                
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model=model_name,
                temperature=temperature
            )
            logger.info("ChatOpenAI успешно инициализирован")
            
            self.chains = PromptChains(
                api_key=api_key,
                model_name=model_name,
                temperature=temperature
            )
            logger.info("PromptChains успешно инициализированы")
            
            # Инициализируем цепочки
            self.analysis_chain = self.chains.create_analysis_chain()
            self.enhancement_chain = self.chains.create_enhancement_chain()
            logger.info("Цепочки успешно инициализированы")
            
            self._errors = []
            logger.info("PromptProcessor успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации PromptProcessor: {str(e)}")
            raise

    def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """Анализирует промпт и возвращает результаты анализа."""
        try:
            # Выполняем анализ
            analysis_result = self.analysis_chain.invoke({"prompt": prompt})
            
            # Если результат уже является словарем, используем его
            if isinstance(analysis_result, dict):
                analysis_dict = analysis_result
            else:
                # Парсим JSON результат
                analysis_dict = parse_json_result(analysis_result)
            
            # Создаем объект PromptAnalysis
            return PromptAnalysis(
                topic=analysis_dict.get("topic", ""),
                style=analysis_dict.get("style", "любой подходящий"),
                format_type=analysis_dict.get("format_type", "любой подходящий"),
                missing_elements=analysis_dict.get("missing_elements", []),
                improvements=analysis_dict.get("improvements", []),
                approaches=analysis_dict.get("approaches", [])
            )
        except Exception as e:
            logger.error(f"Ошибка при анализе промпта: {str(e)}")
            raise APIError(f"Ошибка при анализе промпта: {str(e)}")

    def process_sidebar_data(self, data: Optional[Dict] = None) -> Dict:
        """Обработка данных сайдбара."""
        logger.info(f"Обработка данных сайдбара: {data}")
        
        if not data:
            logger.info("Данные сайдбара не предоставлены, используются значения по умолчанию")
            return {
                "format_type": "любой подходящий",
                "style": "любой подходящий",
                "tone": "любой подходящий",
                "length": "оптимальная"
            }
        
        # Убираем ненужный перевод стилей, так как промпты на русском
        result = {
            "format_type": data.get("format_type", "любой подходящий"),
            "style": data.get("style", "любой подходящий"),
            "tone": data.get("tone", "любой подходящий"),
            "length": data.get("length", "оптимальная длина")
        }
        logger.info(f"Обработанные данные сайдбара: {result}")
        return result

    def analyze_reference_text(self, prompt: str, reference_text: str) -> Dict[str, Any]:
        """Анализирует референсный текст и возвращает результаты анализа."""
        try:
            if not reference_text.strip():
                return {
                    "style": "любой подходящий",
                    "tone": "любой подходящий",
                    "structure": "текст",
                    "key_elements": [],
                    "suggested_prompt": ""
                }

            # Создаем цепочку для анализа референсного текста
            self.reference_chain = self.chains.get_reference_chain_if_applicable({
                "reference_text": reference_text
            })
            
            if not self.reference_chain:
                return {
                    "style": "любой подходящий",
                    "tone": "любой подходящий",
                    "structure": "текст",
                    "key_elements": [],
                    "suggested_prompt": ""
                }

            # Выполняем анализ
            result = self.reference_chain.invoke({"reference_text": reference_text})
            
            # Если результат уже является словарем, используем его
            if isinstance(result, dict):
                return result
                
            # Парсим JSON результат
            return parse_json_result(result)
            
        except Exception as e:
            logger.error(f"Ошибка при анализе референсного текста: {str(e)}")
            return {
                "style": "любой подходящий",
                "tone": "любой подходящий",
                "structure": "любой подходящий",
                "key_elements": [],
                "suggested_prompt": ""
            }

    def enhance_prompt(self, prompt: str, analysis: PromptAnalysis, **kwargs) -> EnhancementResult:
        """Улучшает промпт на основе анализа и дополнительных параметров."""
        try:
            start_time = time.time()
            
            # Получаем параметры форматирования
            format_type = kwargs.get("format_type", analysis.format_type)
            style = kwargs.get("style", analysis.style)
            tone = kwargs.get("tone", "любой подходящий")
            length = kwargs.get("length", "оптимальная")
            
            # Подготавливаем входные данные
            input_data = {
                "prompt": prompt,
                "topic": analysis.topic,
                "style_analysis": analysis.style,
                "format_type_analysis": analysis.format_type,
                "missing_elements": analysis.missing_elements,
                "improvements": analysis.improvements,
                "approaches": analysis.approaches,
                "format_type": format_type,
                "style": style,
                "tone": tone,
                "length": length
            }
            
            # Генерируем улучшенный промпт
            try:
                response = self.enhancement_chain.invoke(input_data)
                logger.debug(f"Ответ от enhancement_chain: {response}")
                
                # Получаем улучшенный промпт
                if isinstance(response, dict):
                    enhanced_prompt = response.get('enhanced_prompt', '')
                else:
                    # Пробуем извлечь текст из JSON строки
                    try:
                        response_dict = json.loads(str(response))
                        enhanced_prompt = response_dict.get('enhanced_prompt', '')
                    except:
                        enhanced_prompt = str(response).strip()
                
                # Очищаем от маркеров кода и JSON
                if enhanced_prompt.startswith("```"):
                    enhanced_prompt = enhanced_prompt.split("```", 1)[1]
                if enhanced_prompt.endswith("```"):
                    enhanced_prompt = enhanced_prompt.rsplit("```", 1)[0]
                enhanced_prompt = enhanced_prompt.strip()
                
                # Удаляем JSON-структуру, если она есть
                if enhanced_prompt.startswith('{') and enhanced_prompt.endswith('}'):
                    try:
                        json_data = json.loads(enhanced_prompt)
                        enhanced_prompt = json_data.get('enhanced_prompt', enhanced_prompt)
                    except:
                        pass
                
                # Проверяем, что улучшенный промпт не пустой
                if not enhanced_prompt:
                    logger.warning("Улучшенный промпт пуст. Используем исходный промпт.")
                    enhanced_prompt = prompt
                
                # Создаем результат
                result = EnhancementResult(
                    original_prompt=prompt,
                    enhanced_prompt=enhanced_prompt,
                    analysis=analysis,
                    improvements=analysis.improvements,
                    approaches=analysis.approaches,
                    processing_time=time.time() - start_time
                )
                
                logger.debug(f"Результат улучшения промпта: {result.enhanced_prompt[:100]}...")
                return result
                
            except Exception as e:
                logger.error(f"Ошибка при вызове enhancement_chain: {str(e)}")
                raise APIError(f"Ошибка при вызове enhancement_chain: {str(e)}")
            
        except Exception as e:
            logger.error(f"Ошибка при улучшении промпта: {str(e)}")
            raise APIError(f"Ошибка при улучшении промпта: {str(e)}")

    def improve_prompt(self, prompt: str, sidebar_data: Optional[Dict] = None, reference_text: Optional[str] = None) -> EnhancementResult:
        """Улучшает промпт с учетом данных сайдбара и референсного текста."""
        try:
            logger.info("Начало улучшения промпта")
            logger.debug(f"Входной промпт: {prompt}")
            logger.debug(f"Данные сайдбара: {sidebar_data}")
            
            # Анализируем промпт
            logger.info("Анализ промпта")
            analysis = self.analyze_prompt(prompt)
            
            # Анализируем референсный текст, если он есть
            reference_analysis = None
            if reference_text:
                logger.info("Анализ референсного текста")
                reference_analysis = self.analyze_reference_text(prompt, reference_text)
            
            # Обрабатываем данные сайдбара
            logger.info("Обработка данных сайдбара")
            sidebar_params = self.process_sidebar_data(sidebar_data)
            
            # Улучшаем промпт
            logger.info("Улучшение промпта")
            result = self.enhance_prompt(
                prompt=prompt,
                analysis=analysis,
                format_type=sidebar_params.get("format_type", "Текст"),
                style=sidebar_params.get("style", "Нейтральный"),
                tone=sidebar_params.get("tone", "Нейтральный"),
                length=sidebar_params.get("length", "Средний"),
                reference_analysis=reference_analysis
            )
            
            logger.info("Промпт успешно улучшен")
            return result
            
        except Exception as e:
            error_msg = f"Ошибка при улучшении промпта: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PromptProcessorError(error_msg)

    def process_prompt(self, prompt: str, sidebar_data: Optional[Dict] = None,
                      reference_text: Optional[str] = None) -> Dict:
        """Полный процесс обработки промпта."""
        start_time = time.time()
        
        try:
            # Анализ промпта
            analysis = self.analyze_prompt(prompt)
            
            # Обработка данных сайдбара
            processed_sidebar = self.process_sidebar_data(sidebar_data)
            
            # Улучшение промпта
            enhanced_prompt = self.enhance_prompt(
                prompt=prompt,
                analysis=analysis,
                **processed_sidebar
            )
            
            processing_time = time.time() - start_time
            
            return {
                "original_prompt": prompt,
                "enhanced_prompt": enhanced_prompt.enhanced_prompt,
                "analysis": analysis.to_dict(),
                "sidebar_data": processed_sidebar,
                "reference_analysis": analysis.to_dict(),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self._handle_error(e, "process_prompt")
            raise

    def _handle_error(self, error: Exception, context: str) -> None:
        """Обработка ошибок."""
        error_message = f"Ошибка в {context}: {str(error)}"
        logger.error(error_message)
        self._errors.append({
            "context": context,
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        })
        raise APIError(error_message) 