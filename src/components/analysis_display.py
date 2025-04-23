import streamlit as st

def display_analysis(analysis_result):
    """Отображает результаты анализа промпта"""
    if not analysis_result:
        st.error("Не удалось получить результаты анализа")
        return
        
    # Отображение основной информации
    st.subheader("📝 Основная информация")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Тема", analysis_result.topic)
    with col2:
        st.metric("Стиль", analysis_result.style)
    with col3:
        st.metric("Формат", analysis_result.format_type)
    
    # Отображение отсутствующих элементов
    if analysis_result.missing_elements:
        st.subheader("❌ Отсутствующие элементы")
        for element in analysis_result.missing_elements:
            st.write(f"• {element}")
    
    # Отображение улучшений
    if analysis_result.improvements:
        st.subheader("✨ Рекомендуемые улучшения")
        for improvement in analysis_result.improvements:
            st.write(f"• {improvement}")
    
    # Отображение подходов
    if analysis_result.approaches:
        st.subheader("🎯 Подходы к улучшению")
        for approach in analysis_result.approaches:
            st.write(f"• {approach}")
            
    # Отображение анализа референсного текста
    if analysis_result.reference_analysis:
        st.subheader("📚 Анализ референсного текста")
        ref_analysis = analysis_result.reference_analysis
        if isinstance(ref_analysis, dict):
            if "style" in ref_analysis:
                st.write(f"**Стиль:** {ref_analysis['style']}")
            if "tone" in ref_analysis:
                st.write(f"**Тон:** {ref_analysis['tone']}")
            if "structure" in ref_analysis:
                st.write(f"**Структура:** {ref_analysis['structure']}")
            if "key_elements" in ref_analysis:
                st.write("**Ключевые элементы:**")
                for element in ref_analysis['key_elements']:
                    st.write(f"• {element}") 