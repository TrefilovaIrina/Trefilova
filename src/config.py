import os
from dotenv import load_dotenv
import logging
import streamlit as st

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Проверка и создание директории для статических файлов
static_dir = 'src/static'
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    logger.info(f"Создана директория для статических файлов: {static_dir}")

# OpenAI Configuration
def get_openai_api_key():
    """Получение API ключа OpenAI с логированием."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY не найден в переменных окружения")
        return None
    logger.info("OPENAI_API_KEY успешно получен из переменных окружения")
    return api_key

OPENAI_API_KEY = get_openai_api_key()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-16k")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "15000"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")
ERROR_LOG_FILE = os.getenv("ERROR_LOG_FILE", "error.log")

# Prompt Configuration
MIN_PROMPT_LENGTH = int(os.getenv("MIN_PROMPT_LENGTH", "10"))
MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "5000"))

# Конфигурация страницы Streamlit
def setup_page():
    st.set_page_config(
        page_title="✨ Promto",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Загрузка CSS стилей
def load_css():
    try:
        with open('src/static/styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Ошибка при загрузке CSS файла: {str(e)}")
        # Загружаем базовые стили в случае ошибки
        st.markdown("""
        <style>
            .main-header { font-size: 1.5rem; color: #1E88E5; text-align: center; }
            .sub-header { font-size: 1.2rem; color: #424242; margin: 1rem 0; }
            h2 { font-size: 1.1rem; margin: 0.8rem 0; }
            h3 { font-size: 1rem; margin: 0.6rem 0; }
        </style>
        """, unsafe_allow_html=True)

def get_config():
    """Получение конфигурации приложения."""
    return {
        "openai_api_key": OPENAI_API_KEY,
        "openai_model": OPENAI_MODEL,
        "openai_temperature": OPENAI_TEMPERATURE,
        "openai_max_tokens": OPENAI_MAX_TOKENS,
        "logging": {
            "level": LOG_LEVEL,
            "file": LOG_FILE,
            "error_file": ERROR_LOG_FILE
        },
        "prompt": {
            "min_length": MIN_PROMPT_LENGTH,
            "max_length": MAX_PROMPT_LENGTH
        }
    } 