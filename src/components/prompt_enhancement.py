import streamlit as st
from src.services.prompt_processor import PromptProcessor
from src.components.analysis_display import display_analysis
from src.utils.prompt_logger import PromptLogger

def display_prompt_enhancement(prompt_processor: PromptProcessor):
    """Отображает интерфейс улучшения промптов"""
    # Инициализируем логгер
    prompt_logger = PromptLogger()
    
    st.markdown('<h3 class="sub-header">✨ Улучшение промптов</h3>', unsafe_allow_html=True)
    
    # Приветственное сообщение и инструкции
    st.markdown('''
    <div class="welcome-box">
        <h3> Hello world! </h3>
        <p>Здесь вы можете улучшить ваши промпты, чтобы получить более точные и полезные ответы от ИИ. Просто вставьте ваш промпт, и мы поможем его оптимизировать.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Пошаговые инструкции
    st.markdown('<h3>Как это работает</h3>', unsafe_allow_html=True)
    st.markdown('''
    <div class="step-box">
        <span class="step-number">1.</span> Вставьте ваш промпт в текстовое поле
    </div>
    <div class="step-box">
        <span class="step-number">2.</span> Настройте параметры улучшения (опционально)
    </div>
    <div class="step-box">
        <span class="step-number">3.</span> Нажмите кнопку "Улучшить промпт"
    </div>
    <div class="step-box">
        <span class="step-number">4.</span> Получите улучшенный промпт и анализ
    </div>
    ''', unsafe_allow_html=True)
    
    # Ввод промпта
    prompt = st.text_area(
        "Введите ваш промпт:",
        placeholder="Вставьте ваш промпт здесь...",
        height=150,
        help="Чем подробнее ваш промпт, тем лучше будут результаты"
    )
    
    # Ограничение длины промпта
    if prompt and len(prompt) > 10000:
        st.warning("⚠️ Ваш промпт слишком длинный. Рекомендуется использовать промпты длиной до 10000 символов.")
        prompt = prompt[:10000]
        st.info("Промпт был автоматически обрезан до 10000 символов.")
    
    # Настройки в сайдбаре
    with st.sidebar:
        st.markdown('<h3 class="sidebar-header">⚙️ Настройки</h3>', unsafe_allow_html=True)
        
        format_type = st.selectbox(
            "Формат:",
            ["Не указано", "Текст", "Список", "Таблица", "JSON", "Другое"],
            help="Выберите формат, в котором вы хотите получить ответ"
        )
        
        style = st.selectbox(
            "Стиль:",
            ["Не указано", "Конфронтационный", "Описательный", "Прямой", "Формальный", "Юмористический", "Влиятельный", "Неформальный", "Вдохновляющий", "Убедительный"],
            help="Выберите стиль написания"
        )
        
        tone = st.selectbox(
            "Тон:",
            ["Не указано", "Профессиональный", "Дружелюбный", "Строгий", "Эмпатичный", "Другое"],
            help="Выберите тон общения"
        )
        
        length = st.selectbox(
            "Длина:",
            ["Не указано", "Краткий", "Средний", "Подробный"],
            help="Выберите желаемую длину ответа"
        )
        
        reference_text = st.text_area(
            "Референсный текст (опционально):",
            height=100,
            help="Вставьте пример текста, стиль которого вы хотите воспроизвести"
        )
        
        # Ограничение длины референсного текста
        if reference_text and len(reference_text) > 10000:
            st.warning("⚠️ Ваш референсный текст слишком длинный. Рекомендуется использовать тексты длиной до 10000 символов.")
            reference_text = reference_text[:10000]
            st.info("Референсный текст был автоматически обрезан до 10000 символов.")
    
    # Кнопка улучшения
    if st.button("✨ Улучшить промпт", key="enhance_prompt_button"):
        if not prompt:
            st.error("❌ Пожалуйста, введите промпт для улучшения.")
            return
        
        with st.spinner("Анализирую и улучшаю промпт..."):
            try:
                # Анализируем промпт
                st.info("🔍 Анализирую промпт...")
                analysis = prompt_processor.analyze_prompt(prompt)
                
                # Отображаем результаты анализа
                with st.expander("📊 Результаты анализа промпта", expanded=True):
                    display_analysis(analysis)
                
                # Отображаем референсный текст, если он был предоставлен
                if reference_text:
                    with st.expander("📝 Референсный текст", expanded=True):
                        st.markdown("### Ваш референсный текст")
                        st.info(reference_text)
                        
                        # Анализируем референсный текст
                        st.markdown("### 📊 Анализ референсного текста")
                        reference_analysis = prompt_processor.analyze_reference_text(prompt, reference_text)
                        
                        # Отображаем результаты анализа референсного текста
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("🎨 Стиль", reference_analysis["style"])
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("🎭 Тон", reference_analysis["tone"])
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown("### 📋 Структура")
                        st.info(reference_analysis["structure"])
                        
                        if reference_analysis["key_elements"]:
                            st.markdown("### 🔑 Ключевые элементы")
                            for element in reference_analysis["key_elements"]:
                                st.markdown(f'<div class="info-box">{element}</div>', unsafe_allow_html=True)
                        
                        if reference_analysis["suggested_prompt"]:
                            st.markdown("### 💡 Предложенный промпт")
                            st.info(reference_analysis["suggested_prompt"])
                
                # Фильтруем параметры, исключая "Не указано"
                sidebar_data = {}
                if format_type != "Не указано":
                    sidebar_data["format_type"] = format_type
                    st.info(f"Выбран формат: {format_type}")
                if style != "Не указано":
                    sidebar_data["style"] = style
                    st.info(f"Выбран стиль: {style}")
                if tone != "Не указано":
                    sidebar_data["tone"] = tone
                    st.info(f"Выбран тон: {tone}")
                if length != "Не указано":
                    sidebar_data["length"] = length
                    st.info(f"Выбрана длина: {length}")
                
                if not sidebar_data:
                    st.info("Параметры сайдбара не указаны, будут использованы значения по умолчанию")
                
                # Улучшаем промпт
                st.info("🔄 Улучшаю промпт...")
                
                # Если нет параметров сайдбара и референсного текста, используем упрощенный вызов
                if not sidebar_data and not reference_text:
                    result = prompt_processor.enhance_prompt(
                        prompt=prompt,
                        analysis=analysis
                    )
                else:
                    result = prompt_processor.improve_prompt(
                        prompt=prompt,
                        sidebar_data=sidebar_data if sidebar_data else None,
                        reference_text=reference_text if reference_text else None
                    )
                
                # Отображаем результат
                st.markdown("### Улучшенный промпт")
                st.code(result.enhanced_prompt, language="text")
                
                # Логируем промпты в файл
                metadata = {
                    "format_type": format_type,
                    "style": style,
                    "tone": tone,
                    "length": length
                }
                prompt_logger.log_prompt(prompt, result.enhanced_prompt, metadata)
                
            except Exception as e:
                st.error(f"❌ Ошибка при обработке промпта: {str(e)}")
                st.error("Пожалуйста, проверьте настройки OpenAI и попробуйте снова.") 