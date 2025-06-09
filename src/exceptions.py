"""Custom exceptions for Claude Memory MCP system"""


class ValidationError(ValueError):
    """Base validation error"""
    pass


class TitleValidationError(ValidationError):
    """Raised when conversation title validation fails"""
    pass


class ContentValidationError(ValidationError):
    """Raised when conversation content validation fails"""
    pass


class DateValidationError(ValidationError):
    """Raised when date validation fails"""
    pass


class QueryValidationError(ValidationError):
    """Raised when search query validation fails"""
    pass