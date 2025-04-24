import streamlit as st
from src.services.idea_processor import IdeaProcessor
from src.utils.clipboard import copy_to_clipboard
from src.models.creative_approaches import CREATIVE_APPROACHES

def display_template(template: str, key: str):
    """Отображает шаблон с кнопкой копирования"""
    # Очищаем текст от лишних пробелов и переносов строк в начале и конце
    template = template.strip()
    
    # Создаем HTML с правильным форматированием
    html = f"""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; max-height: 400px; overflow-y: auto;'>
        <pre style='white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: monospace;'>{template}</pre>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    # Используем уникальный ключ для кнопки копирования
    copy_button_key = f"copy_template_{key}"
    if st.button("📋 Копировать шаблон", key=copy_button_key):
        # Очищаем текст перед копированием
        clean_template = template.strip()
        copy_to_clipboard(clean_template)
        st.success("Шаблон скопирован в буфер обмена!")

def display_idea_generation(idea_processor: IdeaProcessor = None):
    """Отображает компонент генерации идей"""
    st.markdown("## 🎯 Умный выбор метода + генерация промпта")
    
    if idea_processor is None:
        idea_processor = IdeaProcessor()
    
    mode = st.radio(
        "Выберите режим работы:",
        ["Автоматический выбор подхода", "Ручной выбор подхода"],
        help="В автоматическом режиме система сама выберет подходящий подход. В ручном режиме вы можете выбрать подход самостоятельно."
    )
    
    idea = st.text_area(
        "Опишите вашу идею:",
        help="Подробно опишите, что вы хотите сделать. Чем больше деталей вы предоставите, тем лучше система сможет помочь."
    )
    
    context = st.text_area(
        "Дополнительный контекст (необязательно):",
        help="Укажите любую дополнительную информацию, которая может помочь в выборе подхода."
    )
    
    if mode == "Автоматический выбор подхода":
        if st.button("Проанализировать идею"):
            if not idea:
                st.error("Пожалуйста, введите идею для анализа")
                return
                
            try:
                with st.spinner("Анализируем вашу идею..."):
                    result = idea_processor.process_idea(idea, context)
                    st.success("Анализ завершен!")
                    
                    st.markdown("### Ваша идея")
                    st.info(idea)
                    if context:
                        st.markdown("**Дополнительный контекст:**")
                        st.info(context)
                    
                    st.markdown("### Выбранный подход")
                    st.markdown(f"**{result['selected_approach']}**")
                    
                    st.markdown("### Объяснение выбора")
                    st.markdown(result['explanation'])
                    
                    st.markdown("### Шаблон промпта")
                    display_template(result['template'], "copy_template_result")
                    
            except Exception as e:
                st.error(f"Произошла ошибка при анализе идеи: {str(e)}")
                
    else:  # Ручной выбор подхода
        st.markdown("### Доступные подходы")
        for approach_key, approach in CREATIVE_APPROACHES.items():
            st.markdown(f"**{approach.name}**")
            st.markdown(approach.description)
            st.markdown("---")
        
        selected_approach = st.selectbox(
            "Выберите подход:",
            [approach.name for approach in CREATIVE_APPROACHES.values()]
        )
        
        if st.button("Сгенерировать промпт"):
            if not idea:
                st.error("Пожалуйста, введите идею")
                return
                
            try:
                with st.spinner("Генерируем промпт..."):
                    approach = next(
                        (a for a in CREATIVE_APPROACHES.values() if a.name == selected_approach),
                        list(CREATIVE_APPROACHES.values())[0]
                    )
                    
                    st.markdown("### Ваша идея")
                    st.info(idea)
                    if context:
                        st.markdown("**Дополнительный контекст:**")
                        st.info(context)
                    
                    st.markdown("### Шаблон промпта")
                    # Подставляем идею пользователя в шаблон и очищаем от лишних пробелов
                    template_with_idea = approach.prompt_template.format(idea=idea).strip()
                    display_template(template_with_idea, "copy_template_approach")
                        
            except Exception as e:
                st.error(f"Произошла ошибка при генерации промпта: {str(e)}")

def display_idea_card(idea: dict, index: int):
    """Отображает карточку идеи с кнопкой копирования."""
    st.markdown(f'''
    <div class="idea-card">
        <div class="idea-title">Идея #{index}: {idea['title']}</div>
        <div class="idea-description">{idea['description']}</div>
        <div class="idea-tags">
            {''.join([f'<span class="idea-tag">{tag}</span>' for tag in idea['tags']])}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Используем уникальный ключ для кнопки копирования
    copy_button_key = f"copy_idea_card_{index}"
    if st.button("📋 Копировать", key=copy_button_key):
        # Форматируем текст идеи для копирования
        idea_text = f"Идея #{index}: {idea['title']}\n\n{idea['description']}\n\nТеги: {', '.join(idea['tags'])}"
        copy_to_clipboard(idea_text) 