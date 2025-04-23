import streamlit as st
import json
import os
from datetime import datetime

def display_prompt_history():
    """Отображает историю сохраненных промптов"""
    st.markdown("## 📚 История промптов")
    
    try:
        # Загрузка сохраненных промптов
        if os.path.exists('saved_prompts.json'):
            with open('saved_prompts.json', 'r', encoding='utf-8') as f:
                saved_prompts = json.load(f)
        else:
            saved_prompts = []
            
        if not saved_prompts:
            st.info("История промптов пуста. Сохраненные промпты будут отображаться здесь.")
            return
            
        # Отображение промптов
        for i, prompt_data in enumerate(reversed(saved_prompts), 1):
            with st.expander(f"Промпт #{i} - {datetime.fromisoformat(prompt_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"):
                st.text_area("Контекст", prompt_data['context'], height=100, disabled=True)
                st.text_area("Промпт", prompt_data['prompt'], height=200, disabled=True)
                
                # Кнопка копирования
                if st.button("Копировать промпт", key=f"copy_{i}"):
                    st.write(prompt_data['prompt'])
                    st.success("Промпт скопирован в буфер обмена!")
                    
    except Exception as e:
        st.error(f"Ошибка при загрузке истории промптов: {str(e)}") 