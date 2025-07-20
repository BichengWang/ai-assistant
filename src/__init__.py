"""
Private Assistant Chatbot Package
"""

__version__ = "1.0.0"
__author__ = "Private Assistant Team"

from .material_assistant import MaterialAssistant
from .finetune import QAManager
from .profiling import ProfileManager
from .knowledge_base import KnowledgeManager
from .model_management import CheckpointManager

__all__ = [
    'MaterialAssistant',
    'QAManager',
    'ProfileManager', 
    'KnowledgeManager',
    'CheckpointManager'
]