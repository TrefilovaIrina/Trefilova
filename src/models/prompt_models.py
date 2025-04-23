from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class PromptAnalysis(BaseModel):
    """Модель для результатов анализа промпта."""
    topic: str = Field(default="", description="Тема промпта")
    style: str = Field(default="neutral", description="Стиль промпта")
    format_type: str = Field(default="text", description="Тип формата")
    missing_elements: List[str] = Field(default_factory=list, description="Отсутствующие элементы")
    improvements: List[str] = Field(default_factory=list, description="Предлагаемые улучшения")
    approaches: List[str] = Field(default_factory=list, description="Подходы к улучшению")
    reference_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Анализ референсного текста")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        return {
            "topic": self.topic,
            "style": self.style,
            "format_type": self.format_type,
            "missing_elements": self.missing_elements,
            "improvements": self.improvements,
            "approaches": self.approaches,
            "reference_analysis": self.reference_analysis
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptAnalysis":
        """Создает объект из словаря."""
        return cls(**data)

class EnhancementResult(BaseModel):
    """Модель для результатов улучшения промпта."""
    original_prompt: str = Field(..., description="Исходный промпт")
    enhanced_prompt: str = Field(..., description="Улучшенный промпт")
    analysis: PromptAnalysis = Field(..., description="Результаты анализа")
    improvements: List[str] = Field(default_factory=list, description="Внесенные улучшения")
    approaches: List[str] = Field(default_factory=list, description="Использованные подходы")
    processing_time: float = Field(default=0.0, description="Время обработки в секундах")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время создания результата")

    @validator("original_prompt", "enhanced_prompt")
    def validate_prompts(cls, v: str) -> str:
        """Проверяет, что промпты не пустые."""
        if not v.strip():
            raise ValueError("Промпт не может быть пустым")
        return v.strip()

    @validator("timestamp", pre=True)
    def set_timestamp(cls, v: Optional[datetime]) -> datetime:
        """Устанавливает текущее время, если не указано."""
        return v or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        return {
            "original_prompt": self.original_prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "analysis": self.analysis.to_dict(),
            "improvements": self.improvements,
            "approaches": self.approaches,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancementResult":
        """Создает объект из словаря."""
        if "analysis" in data and isinstance(data["analysis"], dict):
            data["analysis"] = PromptAnalysis.from_dict(data["analysis"])
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data) 