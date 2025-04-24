from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence, RunnablePassthrough
from typing import Optional, Dict, Any
import json
import logging
from ..config import OPENAI_MAX_TOKENS, OPENAI_MODEL, OPENAI_TEMPERATURE


logger = logging.getLogger(__name__)

class PromptChains:
    """Класс для создания цепочек анализа и улучшения промптов."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = OPENAI_MODEL, temperature: float = OPENAI_TEMPERATURE):
        """Инициализация цепочек промптов."""
        try:
            if not api_key:
                raise ValueError("OPENAI_API_KEY не установлен")
                
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model=model_name,
                temperature=temperature
            )
            logger.info("ChatOpenAI успешно инициализирован в PromptChains")
        except Exception as e:
            logger.error(f"Ошибка при инициализации PromptChains: {str(e)}")
            raise

    def create_analysis_chain(self) -> RunnableSequence:
        """
        Создает цепочку для анализа промпта.
        
        Returns:
            RunnableSequence: Цепочка для анализа промпта.
        """
        template_str = """
Проанализируй следующий промпт и разложи его на ключевые элементы, необходимые для его улучшения. Используй следующие шаги:

1. Определи основную **тему** и предполагаемую **роль** исполнителя (например: "Ты — эксперт по маркетингу").
2. Укажи предполагаемый **стиль изложения** (формальный, неформальный, технический, академический и т.п.).
3. Определи, в каком **формате** предполагается получить ответ (инструкция, статья, список, эссе и др.).
4. Перечисли самые важные **отсутствующие элементы**, которые мешают понять или выполнить запрос (например: нет роли, нет инструкции по структуре, нет примеров).
5. Предложи **конкретные улучшения**, которые сделают промпт соответствующим 5 принципам эффективного промт-инжиниринга:
   - Чёткость и направленность задачи,
   - Форматированность и структура,
   - Наличие примеров,
   - Логическая разбивка на шаги,
   - Понятность и измеримость результата.
6. Укажи **подходы и стратегии**, которые помогут повысить эффективность промпта.

Если какая-либо информация в промпте не указана явно, **предложи наиболее эффективный и релевантный вариант**, исходя из логики задачи и лучших практик построения промптов.

Промпт: {prompt}

Верни результат в формате JSON:
{{
  "topic": "тема и предполагаемая роль исполнителя",
  "style": "предполагаемый стиль изложения",
  "format_type": "формат предполагаемого ответа",
  "missing_elements": ["элемент1", "элемент2"],
  "improvements": ["улучшение1", "улучшение2"],
  "approaches": ["подход1", "подход2"]
}}
"""
        template = PromptTemplate(template=template_str, input_variables=["prompt"])

        def parse_response(response: Any) -> Dict[str, Any]:
            """
            Парсит ответ от LLM и возвращает структурированные данные.
            
            Args:
                response: Ответ от LLM.
                
            Returns:
                Dict[str, Any]: Структурированные данные с анализом промпта.
            """
            try:
                content = getattr(response, "content", str(response))
                logger.debug(f"Получен ответ от LLM: {content[:200]}...")  # Логируем первые 200 символов
                
                if isinstance(content, dict):
                    logger.debug("Ответ уже в формате словаря")
                    return content
                
                # Если content - это строка, пробуем распарсить её как JSON
                if isinstance(content, str):
                    try:
                        # Очищаем строку от возможных лишних символов
                        content = content.strip()
                        if content.startswith("```json"):
                            logger.debug("Найден блок JSON кода, удаляю маркеры")
                            content = content[7:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()
                        
                        result = json.loads(content)
                        logger.debug(f"JSON успешно распарсен, ключи: {result.keys()}")
                        return result
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка парсинга JSON: {str(e)}, предпросмотр контента: {content[:100]}...")
                
                logger.warning(f"Неожиданный тип контента: {type(content)}")
                return {
                    "topic": "",
                    "style": "любой подходящий",
                    "format_type": "любой подходящий",
                    "missing_elements": [],
                    "improvements": [],
                    "approaches": []
                }
            except Exception as e:
                logger.error(f"Неожиданная ошибка при парсинге ответа: {str(e)}")
                return {
                    "topic": "",
                    "style": "любой подходящий",
                    "format_type": "любой подходящий",
                    "missing_elements": [],
                    "improvements": [],
                    "approaches": []
                }

        chain = (
            {"prompt": lambda x: str(x.get("prompt", "")).strip()}
            | template
            | self.llm
            | parse_response
        )
        
        logger.debug("Цепочка для анализа промпта создана успешно")
        return chain

    def create_enhancement_chain(self) -> RunnableSequence:
        """
        Создает цепочку для улучшения промпта.
        
        Returns:
            RunnableSequence: Цепочка для улучшения промпта.
        """
        template = PromptTemplate(
            template="""
Ты — эксперт по промт-инжинирингу. Твоя задача — переписать пользовательский промпт так, чтобы он стал максимально эффективным и соответствовал 5 ключевым принципам:

1. Чёткость и направленность: ясно сформулируй цель и укажи роль исполнителя (например: "Ты — эксперт по маркетингу").
2. Структурированность: определи формат ответа (инструкция, список, эссе и т.д.) и задай логичную структуру.
3. Примеры: добавь примеры, если они помогут лучше понять задачу.
4. Разделение на шаги: при необходимости разбей задачу на логические блоки.
5. Понятный и измеримый результат: уточни, что именно должен сделать LLM и в каком виде выдать ответ.

ВАЖНО: Твой улучшенный промпт должен быть оптимальной длины и содержать все необходимые детали. Не сокращай его и не пропускай важные элементы.

---

**Исходный промпт:**
{prompt}

- Тема и направление пользовательской задачи: {topic}
- Ответ нужно получить в таком стиле: {style_analysis}
- Формат решения этой задачи это: {format_type_analysis}
- Добавь в промпт недостающие элементы для постановки задачи: {missing_elements}
- Реализуй в промпте такие элементы в постановке задачи: {improvements}
- Наилучший подход к решению этой задачи: {approaches}

**Пользователь хочет составить такой промт чтобы после его отработки результат соотвествовал таким параметрам:**
{format_type_instruction}
{style_instruction}
{tone_instruction}
{length_instruction}

Если какая-либо информация отсутствует или не определена, выбери наиболее подходящий и эффективный вариант, исходя из логики задачи и лучших практик промт-инжиниринга.
Перед отправкой проверь промт на эффективность и соотвествие 5 принципам эффективного промт-инжиниринга.
ВАЖНО: 
1. Улучшенный промпт должен быть подробным и содержать все необходимые детали
2. Включи все важные элементы из анализа
3. Добавь конкретные примеры и инструкции
4. Укажи четкую структуру и формат ответа
5. Не сокращай промпт, даже если исходный был коротким

---

Верни только улучшенный промпт, без дополнительных атрибутов и метаданных. Не используй JSON формат, просто верни текст улучшенного промпта.
""",
            input_variables=[
                "prompt", "topic", "style_analysis", "format_type_analysis",
                "missing_elements", "improvements", "approaches",
                "format_type_instruction", "style_instruction", "tone_instruction", "length_instruction"
            ]
        )

        def parse_response(response: Any) -> Dict[str, Any]:
            """
            Парсит ответ от LLM и возвращает структурированные данные.
            
            Args:
                response: Ответ от LLM.
                
            Returns:
                Dict[str, Any]: Структурированные данные с улучшенным промптом.
            """
            try:
                content = getattr(response, "content", str(response))
                logger.debug(f"Получен ответ от LLM: {content[:200]}...")  # Логируем первые 200 символов
                
                # Очищаем строку от возможных лишних символов
                content = content.strip()
                
                # Удаляем маркеры кода, если они есть
                if content.startswith("```"):
                    content = content.split("```", 1)[1]
                if content.endswith("```"):
                    content = content.rsplit("```", 1)[0]
                content = content.strip()
                
                # Возвращаем только enhanced_prompt
                return {
                    "enhanced_prompt": content
                }
            except Exception as e:
                logger.error(f"Неожиданная ошибка при парсинге ответа: {str(e)}")
                return {
                    "enhanced_prompt": str(response)
                }

        chain = (
            RunnablePassthrough.assign(
                format_type_instruction=lambda x: f"- В каком формате нужен результат: {x.get('format_type', 'любой подходящий')}" if x.get('format_type') else "",
                style_instruction=lambda x: f"- В каком стиле пользователь хочет получить результат: {x.get('style', 'любой подходящий')}" if x.get('style') else "",
                tone_instruction=lambda x: f"- Какую тональность: {x.get('tone', 'любой подходящий')}" if x.get('tone') else "",
                length_instruction=lambda x: f"- Предпочтительная длина ответа от LLM после отработки промта: {x.get('length', 'оптимальная длина')}" if x.get('length') else ""
            )
            | template
            | self.llm
            | parse_response
        )
        
        logger.debug("Цепочка для улучшения промпта создана успешно")
        return chain

    def get_reference_chain_if_applicable(self, data: Dict[str, Any]) -> Optional[RunnableSequence]:
        """
        Создает цепочку для анализа референсного текста, если он предоставлен.
        
        Args:
            data: Словарь с входными данными, включая референсный текст.
            
        Returns:
            Optional[RunnableSequence]: Цепочка для анализа референсного текста или None,
            если референсный текст не предоставлен.
        """
        reference_text = data.get("reference_text", "").strip()
        if not reference_text:
            logger.debug("Референсный текст не предоставлен")
            return None

        logger.debug(f"Создаю цепочку для анализа референсного текста длиной {len(reference_text)} символов")

        template = PromptTemplate(
            template="""
Проанализируй следующий референсный текст и создай промпт, который приведет к аналогичному результату.

Референсный текст:
{reference_text}

Верни результат в формате JSON:
{{
  "style": "описание стиля",
  "tone": "описание тона",
  "structure": "описание структуры",
  "key_elements": ["элемент1", "элемент2"],
  "suggested_prompt": "предложенный промпт"
}}
""",
            input_variables=["reference_text"]
        )

        def parse_response(response: Any) -> Dict[str, Any]:
            """
            Парсит ответ от LLM и возвращает структурированные данные.
            
            Args:
                response: Ответ от LLM.
                
            Returns:
                Dict[str, Any]: Структурированные данные с анализом референсного текста.
            """
            try:
                content = getattr(response, "content", str(response))
                logger.debug(f"Получен ответ от LLM: {content[:200]}...")  # Логируем первые 200 символов
                
                if isinstance(content, dict):
                    logger.debug("Ответ уже в формате словаря")
                    return content
                
                # Если content - это строка, пробуем распарсить её как JSON
                if isinstance(content, str):
                    try:
                        # Очищаем строку от возможных лишних символов
                        content = content.strip()
                        if content.startswith("```json"):
                            logger.debug("Найден блок JSON кода, удаляю маркеры")
                            content = content[7:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()
                        
                        result = json.loads(content)
                        logger.debug(f"JSON успешно распарсен, ключи: {result.keys()}")
                        return result
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка парсинга JSON: {str(e)}, предпросмотр контента: {content[:100]}...")
                
                logger.warning(f"Неожиданный тип контента: {type(content)}")
                return {
                    "style": "любой подходящий",
                    "tone": "любой подходящий",
                    "structure": "любая подходящая",
                    "key_elements": [],
                    "suggested_prompt": str(content)  # Используем исходный контент как suggested_prompt
                }
            except Exception as e:
                logger.error(f"Неожиданная ошибка при парсинге ответа: {str(e)}")
                return {
                    "style": "любой подходящий",
                    "tone": "любой подходящий",
                    "structure": "любой подходящий",
                    "key_elements": [],
                    "suggested_prompt": ""
                }

        chain = (
            RunnablePassthrough.assign(
                reference_text=lambda x: str(x.get("reference_text", "")).strip()
            )
            | template
            | self.llm
            | parse_response
        )
        
        logger.debug("Цепочка для анализа референсного текста создана успешно")
        return chain
