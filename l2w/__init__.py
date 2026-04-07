"""l2w - Linux-to-Windows command translator."""

from .commands import COMMAND_MAP, CommandDef
from .translator import Translator, TranslationError
from .executor import Executor, ExecutionResult

__version__ = "1.0.0"
__all__ = [
    "COMMAND_MAP",
    "CommandDef",
    "Translator",
    "TranslationError",
    "Executor",
    "ExecutionResult",
]
