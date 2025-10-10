"""Custom exceptions for Claude Memory MCP system"""


class ValidationError(ValueError):
    """Base validation error"""


class TitleValidationError(ValidationError):
    """Raised when conversation title validation fails"""


class ContentValidationError(ValidationError):
    """Raised when conversation content validation fails"""


class DateValidationError(ValidationError):
    """Raised when date validation fails"""


class QueryValidationError(ValidationError):
    """Raised when search query validation fails"""
