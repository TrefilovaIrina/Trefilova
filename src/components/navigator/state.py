import json
import os
import logging
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def load_saved_prompts() -> list:
    """Загружает сохраненные промпты из файла."""
    try:
        if os.path.exists('saved_prompts.json'):
            with open('saved_prompts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Ошибка при загрузке сохраненных промптов: {str(e)}")
        return []

def save_prompt(prompt: str) -> bool:
    """Сохраняет промпт в файл."""
    try:
        saved_prompts = load_saved_prompts()
        saved_prompts.append({
            'prompt': prompt,
            'timestamp': datetime.now().isoformat(),
            'context': st.session_state.get('task', '')
        })
        
        with open('saved_prompts.json', 'w', encoding='utf-8') as f:
            json.dump(saved_prompts, f, ensure_ascii=False, indent=2)
            
        st.session_state.saved_prompts = saved_prompts
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении промпта: {str(e)}")
        return False

def reset_session_state() -> None:
    """Сбрасывает состояние сессии."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.current_step = 1

def initialize_session_state() -> None:
    """Инициализация состояния сессии."""
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    if "task" not in st.session_state:
        st.session_state.task = ""
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "analysis" not in st.session_state:
        st.session_state.analysis = None
    if "saved_prompts" not in st.session_state:
        st.session_state.saved_prompts = load_saved_prompts()

def save_task(task: str) -> None:
    """Сохраняет задачу в состояние сессии."""
    st.session_state.task = task

def load_task() -> str:
    """Загружает задачу из состояния сессии."""
    return st.session_state.get('task', '')

def save_questions(questions: List[str]) -> None:
    """Сохраняет вопросы в состояние сессии."""
    st.session_state.questions = questions

def load_questions() -> List[str]:
    """Загружает вопросы из состояния сессии."""
    return st.session_state.get('questions', [])

def save_answers(answers: Dict[str, str]) -> None:
    """Сохраняет ответы в состояние сессии."""
    st.session_state.answers = answers

def load_answers() -> Dict[str, str]:
    """Загружает ответы из состояния сессии."""
    return st.session_state.get('answers', {})

def save_analysis(analysis: Dict[str, Any]) -> None:
    """Сохраняет анализ в состояние сессии."""
    st.session_state.analysis = analysis

def load_analysis() -> Optional[Dict[str, Any]]:
    """Загружает анализ из состояния сессии."""
    return st.session_state.get('analysis', None)

def load_prompt() -> str:
    """Загружает промпт из состояния сессии."""
    return st.session_state.get('prompt', '')

def save_prompt_to_session(prompt: str) -> None:
    """Сохраняет промпт в состоянии сессии."""
    st.session_state['prompt'] = prompt 