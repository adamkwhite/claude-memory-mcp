"""
JSON Schema validation for Universal Memory MCP.

Provides validation schemas for different AI platform export formats.
"""

from .chatgpt_schema import CHATGPT_SCHEMA, validate_chatgpt_export
from .cursor_schema import CURSOR_SCHEMA, validate_cursor_export
from .claude_schema import CLAUDE_SCHEMA, validate_claude_export
from .universal_schema import UNIVERSAL_SCHEMA, validate_universal_conversation

__all__ = [
    'CHATGPT_SCHEMA',
    'CURSOR_SCHEMA', 
    'CLAUDE_SCHEMA',
    'UNIVERSAL_SCHEMA',
    'validate_chatgpt_export',
    'validate_cursor_export',
    'validate_claude_export',
    'validate_universal_conversation'
]