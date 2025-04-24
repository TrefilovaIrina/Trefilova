from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CreativeApproach(BaseModel):
    """Модель для описания творческого подхода"""
    name: str = Field(..., description="Название подхода")
    description: str = Field(..., description="Описание подхода")
    prompt_template: str = Field(..., description="Шаблон промпта для этого подхода")
    is_active: bool = Field(default=True, description="Активен ли подход")

class IdeaRequest(BaseModel):
    """Модель для запроса на генерацию идеи"""
    idea: str = Field(..., description="Идея для обработки")
    context: Optional[str] = Field(None, description="Дополнительный контекст для идеи")

class IdeaResponse(BaseModel):
    """Модель для ответа с промптом"""
    selected_approach: CreativeApproach = Field(..., description="Выбранный подход")
    generated_prompt: str = Field(..., description="Сгенерированный промпт")
    explanation: str = Field(..., description="Объяснение выбора подхода")

class Idea(BaseModel):
    """Модель для идеи."""
    title: str = Field(..., description="Заголовок идеи")
    description: str = Field(..., description="Описание идеи")
    tags: List[str] = Field(default_factory=list, description="Теги, характеризующие идею")
    approach: str = Field(..., description="Использованный креативный подход")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания идеи")

class IdeaGenerationRequest(BaseModel):
    """Модель для запроса на генерацию идей."""
    task: str = Field(..., description="Задача, для которой нужно сгенерировать идеи")
    num_ideas: int = Field(default=5, description="Количество идей для генерации")
    category: Optional[str] = Field(default=None, description="Категория идей")

class IdeaGenerationResult(BaseModel):
    """Модель для результата генерации идей."""
    ideas: List[Idea] = Field(..., description="Сгенерированные идеи")
    selected_approach: str = Field(..., description="Выбранный креативный подход")
    processing_time: float = Field(default=0.0, description="Время обработки в секундах")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время создания результата")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        return {
            "ideas": [{"title": idea.title, "description": idea.description, "tags": idea.tags, "approach": idea.approach} for idea in self.ideas],
            "selected_approach": self.selected_approach,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat()
        } 