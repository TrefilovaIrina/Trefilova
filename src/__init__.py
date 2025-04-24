"""
Prompt Enhancer - инструмент для анализа и улучшения промптов.
"""

from .models.prompt_models import PromptAnalysis, EnhancementResult
from .chains.fixed_prompt_chains import PromptChains

__version__ = "1.0.0"
__all__ = ['PromptAnalysis', 'EnhancementResult', 'PromptChains'] 