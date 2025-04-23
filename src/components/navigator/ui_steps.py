import streamlit as st
import logging
from src.services.prompt_processor import PromptProcessor
from src.utils.clipboard import copy_to_clipboard
from .navigator import PromptNavigator
from .state import (
    load_saved_prompts,
    save_prompt,
    save_prompt_to_session,
    reset_session_state,
    initialize_session_state,
    save_task,
    load_task,
    save_questions,
    load_questions,
    save_answers,
    load_answers,
    save_analysis,
    load_analysis
)
import os

logger = logging.getLogger(__name__)

def get_navigator(prompt_processor: PromptProcessor) -> PromptNavigator:
    """Get or create PromptNavigator instance."""
    if 'navigator' not in st.session_state:
        # Получаем API ключ из состояния сессии
        api_key = st.session_state.get('openai_api_key')
        if not api_key:
            raise ValueError("API ключ не найден в состоянии сессии")
        st.session_state['navigator'] = PromptNavigator(api_key=api_key)
    return st.session_state['navigator']

def display_prompt_navigator(prompt_processor: PromptProcessor) -> None:
    """Отображение интерфейса навигатора промптов."""
    try:
        # Инициализация состояния сессии
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 1
            st.session_state.task = ""
            st.session_state.answers = {}
            st.session_state.generated_prompt = ""
            logger.info("Инициализировано начальное состояние навигатора")
            
        # Получаем навигатор
        navigator = get_navigator(prompt_processor)
        
        # Логируем текущий шаг
        logger.info(f"Текущий шаг: {st.session_state.current_step}")
        
        # Отображаем текущий шаг
        if st.session_state.current_step == 1:
            logger.info("Отображаем шаг 1")
            display_step_1(navigator)
        elif st.session_state.current_step == 2:
            logger.info("Отображаем шаг 2")
            display_step_2(navigator)
        elif st.session_state.current_step == 3:
            logger.info("Отображаем шаг 3")
            display_step_3(navigator)
        elif st.session_state.current_step == 4:
            logger.info("Отображаем шаг 4")
            display_step_4(navigator)
            
    except Exception as e:
        logger.error(f"Ошибка в навигаторе промптов: {str(e)}")
        st.error("Произошла ошибка. Пожалуйста, попробуйте еще раз.")

def display_step_1(navigator: PromptNavigator) -> None:
    """Отображение первого шага - ввод задачи."""
    st.header("Шаг 1: Введите вашу задачу")
    
    # Поле для ввода задачи
    task = st.text_area(
        "Опишите вашу задачу максимально подробно",
        value=st.session_state.task,
        height=150
    )
    
    if st.button("Сгенерировать вопросы"):
        if not task.strip():
            st.error("Пожалуйста, введите описание задачи")
            return
            
        try:
            with st.spinner("Генерация уточняющих вопросов..."):
                # Генерируем вопросы
                questions = navigator.generate_clarifying_questions(task)
                
                if not questions:
                    st.error("""
                    Не удалось сгенерировать вопросы. Возможные причины:
                    - Задача слишком короткая или неясная
                    - Проблемы с подключением к API
                    - Недостаточно контекста для генерации вопросов
                    
                    Пожалуйста:
                    1. Убедитесь, что задача описана подробно
                    2. Проверьте подключение к интернету
                    3. Попробуйте переформулировать задачу
                    """)
                    return
                    
                # Сохраняем состояние
                st.session_state.task = task
                st.session_state.questions = questions
                st.session_state.current_step = 2
                st.rerun()
                
        except Exception as e:
            logger.error(f"Ошибка при генерации вопросов: {str(e)}")
            st.error(f"""
            Произошла ошибка при генерации вопросов:
            {str(e)}
            
            Пожалуйста:
            1. Проверьте подключение к интернету
            2. Убедитесь, что API ключ правильно настроен
            3. Попробуйте еще раз через несколько секунд
            """)

def display_step_2(navigator: PromptNavigator) -> None:
    """Отображение второго шага - ответы на вопросы."""
    st.header("Шаг 2: Ответьте на уточняющие вопросы")
    
    # Отображаем вопросы и поля для ответов
    answers = {}
    for i, question in enumerate(st.session_state.questions):
        answer = st.text_area(
            f"Вопрос {i+1}: {question}",
            value=st.session_state.answers.get(question, ""),
            key=f"answer_{i}"
        )
        answers[question] = answer
    
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("Проанализировать")
    
    # Если есть сохраненный анализ, показываем его
    if 'analysis' in st.session_state:
        st.success("Анализ успешно завершен!")
        st.subheader("Результаты анализа:")
        
        analysis = st.session_state.analysis
        st.write("**Тип задачи:**")
        st.write(analysis.get('task_type', 'Не определен'))
        
        st.write("**Подход к решению:**")
        st.write(analysis.get('approach', 'Не определен'))
        
        st.write("**Шаги решения:**")
        for step in analysis.get('steps', []):
            with st.expander(f"Шаг {step.get('step_number')}"):
                st.write(f"**Описание:** {step.get('description')}")
                st.write(f"**Рекомендуемая модель:** {step.get('llm')}")
                st.write(f"**Промпт для шага:**")
                st.code(step.get('step_prompt'), language='text')
        
        st.write("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            next_button = st.button("Продолжить →")
            if next_button:
                logger.info("Нажата кнопка 'Продолжить', переходим к шагу 3")
                st.session_state.current_step = 3
                st.experimental_rerun()
    
    if analyze_button:
        logger.info("Нажата кнопка 'Проанализировать'")
        # Проверяем, что все вопросы имеют ответы
        if not all(answers.values()):
            st.error("Пожалуйста, ответьте на все вопросы")
            return
            
        try:
            with st.spinner("Анализ ответов..."):
                # Анализируем задачу
                analysis = navigator.analyze_task(st.session_state.task, answers)
                
                if not analysis:
                    st.error("Не удалось проанализировать задачу. Пожалуйста, попробуйте еще раз.")
                    return
                    
                # Сохраняем состояние
                st.session_state.answers = answers
                st.session_state.analysis = analysis
                logger.info("Анализ успешно сохранен в состоянии")
                st.experimental_rerun()
                
        except Exception as e:
            logger.error(f"Ошибка при анализе задачи: {str(e)}")
            st.error("Произошла ошибка при анализе задачи. Пожалуйста, попробуйте еще раз.")

def display_step_2_1(navigator: PromptNavigator) -> None:
    """Отображение шага 2.1 - подтверждение анализа."""
    st.header("Шаг 2.1: Проверьте анализ задачи")
    
    analysis = st.session_state.get('analysis')
    if not analysis:
        st.error("Анализ не найден. Пожалуйста, вернитесь к предыдущему шагу.")
        return
        
    # Отображаем результаты анализа
    st.subheader("Тип задачи:")
    st.write(analysis.get('task_type', 'Не определен'))
    
    st.subheader("Подход к решению:")
    st.write(analysis.get('approach', 'Не определен'))
    
    st.subheader("Шаги решения:")
    for step in analysis.get('steps', []):
        st.write(f"Шаг {step.get('step_number')}: {step.get('description')}")
        st.write(f"Рекомендуемая модель: {step.get('llm')}")
        st.write("---")
    
    # Кнопки для навигации
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Вернуться к вопросам"):
            st.session_state.current_step = 2
            st.rerun()
            
    with col2:
        if st.button("Подтвердить и продолжить"):
            st.session_state.current_step = 3
            st.rerun()

def display_step_3(navigator: PromptNavigator) -> None:
    """Отображение третьего шага - генерация промпта."""
    logger.info("Начало отображения шага 3")
    st.header("Шаг 3: Генерация промпта")
    
    # Получаем данные из предыдущих шагов
    task = st.session_state.get('task')
    analysis = st.session_state.get('analysis')
    
    if not task or not analysis:
        logger.error("Отсутствуют необходимые данные для шага 3")
        st.error("Отсутствуют необходимые данные. Пожалуйста, вернитесь к началу.")
        return
        
    logger.info("Данные для шага 3 успешно получены")
    
    # Отображаем текущий анализ для подтверждения
    st.subheader("Текущий анализ задачи:")
    
    st.write("**Тип задачи:**")
    st.write(analysis.get('task_type', 'Не определен'))
    
    st.write("**Подход к решению:**")
    st.write(analysis.get('approach', 'Не определен'))
    
    st.write("**Шаги решения:**")
    for step in analysis.get('steps', []):
        with st.expander(f"Шаг {step.get('step_number')}"):
            st.write(f"**Описание:** {step.get('description')}")
            st.write(f"**Рекомендуемая модель:** {step.get('llm')}")
            st.write(f"**Промпт для шага:**")
            st.code(step.get('step_prompt'), language='text')
    
    # Кнопка для генерации промпта
    if st.button("Сгенерировать промпт"):
        logger.info("Нажата кнопка 'Сгенерировать промпт'")
        try:
            with st.spinner("Генерируем промпт..."):
                generated_prompt = navigator.generate_prompt(task, analysis)
                if generated_prompt:
                    st.session_state.generated_prompt = generated_prompt
                    st.session_state.current_step = 4
                    logger.info("Промпт успешно сгенерирован, переходим к шагу 4")
                    st.experimental_rerun()
                else:
                    logger.error("Не удалось сгенерировать промпт")
                    st.error("Не удалось сгенерировать промпт. Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            logger.error(f"Ошибка при генерации промпта: {str(e)}")
            st.error("Произошла ошибка при генерации промпта. Пожалуйста, попробуйте еще раз.")
            
    # Кнопка для возврата к предыдущему шагу
    if st.button("← Вернуться к ответам"):
        logger.info("Возврат к шагу 2")
        st.session_state.current_step = 2
        st.experimental_rerun()

def display_step_4(navigator: PromptNavigator) -> None:
    """Отображение сгенерированного промпта и опций для сохранения или регенерации."""
    st.header("Шаг 4: Сгенерированный промпт")
    
    # Проверяем наличие сгенерированного промпта
    if not st.session_state.generated_prompt:
        st.error("Промпт не был сгенерирован. Пожалуйста, вернитесь к предыдущему шагу.")
        if st.button("Вернуться к шагу 3"):
            st.session_state.current_step = 3
            st.rerun()
        return
    
    # Отображаем сгенерированный промпт
    st.subheader("Ваш промпт:")
    st.text_area("Сгенерированный промпт", st.session_state.generated_prompt, height=200)
    
    # Кнопки для действий с промптом
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Сохранить промпт"):
            try:
                # Используем функцию save_prompt для сохранения промпта
                if save_prompt(st.session_state.generated_prompt):
                    st.success("Промпт успешно сохранен!")
                else:
                    st.error("Не удалось сохранить промпт. Пожалуйста, попробуйте еще раз.")
            except Exception as e:
                logger.error(f"Ошибка при сохранении промпта: {str(e)}")
                st.error("Не удалось сохранить промпт. Пожалуйста, попробуйте еще раз.")
    
    with col2:
        if st.button("Сгенерировать новый промпт"):
            st.session_state.current_step = 3
            st.rerun()
    
    with col3:
        if st.button("Начать заново"):
            st.session_state.current_step = 1
            st.session_state.task = ""
            st.session_state.answers = {}
            st.session_state.generated_prompt = ""
            st.rerun()
    
    # Добавляем кнопку для копирования промпта в буфер обмена
    if st.button("Копировать промпт в буфер обмена"):
        try:
            if copy_to_clipboard(st.session_state.generated_prompt):
                st.success("Промпт успешно скопирован в буфер обмена!")
            else:
                st.error("Не удалось скопировать промпт в буфер обмена. Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            logger.error(f"Ошибка при копировании промпта в буфер обмена: {str(e)}")
            st.error("Не удалось скопировать промпт в буфер обмена. Пожалуйста, попробуйте еще раз.")
    
    # Добавляем кнопку для просмотра истории промптов
    if st.button("Просмотреть историю промптов"):
        from src.components.prompt_history import display_prompt_history 