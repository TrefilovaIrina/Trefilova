from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from datetime import datetime

# Создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass

class PromptLog(Base):
    """Модель для хранения логов промптов"""
    __tablename__ = 'prompt_logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    original_prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=False)
    prompt_metadata = Column(JSON)

def init_db():
    """Инициализация базы данных"""
    # Получаем URL базы данных из переменных окружения
    # В Streamlit Community Cloud это будет предоставлено автоматически
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Для локальной разработки используем SQLite
        database_url = 'sqlite:///prompt_logs.db'
    
    # Создаем движок базы данных
    engine = create_engine(database_url)
    
    # Создаем таблицы
    Base.metadata.create_all(engine)
    
    # Создаем фабрику сессий
    Session = sessionmaker(bind=engine)
    
    return Session()

def log_prompt(session, original_prompt: str, enhanced_prompt: str, metadata: dict = None):
    """Сохранение промпта в базу данных"""
    log = PromptLog(
        original_prompt=original_prompt,
        enhanced_prompt=enhanced_prompt,
        prompt_metadata=metadata
    )
    session.add(log)
    session.commit()

def get_logs(session, limit: int = None):
    """Получение логов из базы данных"""
    query = session.query(PromptLog).order_by(PromptLog.timestamp.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

def clear_logs(session):
    """Очистка всех логов"""
    session.query(PromptLog).delete()
    session.commit() 