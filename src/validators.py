"""Input validation for Claude Memory MCP system"""

import re
from datetime import datetime
from typing import Optional

try:
    from .exceptions import (
        ValidationError,
        TitleValidationError,
        ContentValidationError,
        DateValidationError,
        QueryValidationError
    )
except ImportError:
    # For direct imports during testing
    from exceptions import (
        ValidationError,
        TitleValidationError,
        ContentValidationError,
        DateValidationError,
        QueryValidationError
    )

# Constants for validation
MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 1_000_000  # 1MB limit
MAX_QUERY_LENGTH = 500
MIN_CONTENT_LENGTH = 1

# Dangerous patterns to prevent security issues
PATH_TRAVERSAL_PATTERN = re.compile(r'\.{2}[/\\]|[/\\]\.{2}')
NULL_BYTE_PATTERN = re.compile(r'\x00')
CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x1F\x7F]')  # Except newline, tab, CR
SAFE_CONTROL_CHARS = {'\n', '\r', '\t'}


def validate_title(title: Optional[str]) -> str:
    """
    Validate and sanitize conversation title
    
    Args:
        title: The title to validate
        
    Returns:
        Sanitized title string
        
    Raises:
        TitleValidationError: If title is invalid
    """
    if not title:
        return "Untitled Conversation"
    
    # Check length
    if len(title) > MAX_TITLE_LENGTH:
        raise TitleValidationError(
            f"Title too long: {len(title)} characters (max {MAX_TITLE_LENGTH})"
        )
    
    # Check for null bytes
    if NULL_BYTE_PATTERN.search(title):
        raise TitleValidationError("Title contains null bytes")
    
    # Check for path traversal attempts
    if PATH_TRAVERSAL_PATTERN.search(title):
        raise TitleValidationError("Title contains invalid path characters")
    
    # Remove control characters except safe ones
    cleaned_title = ''.join(
        char for char in title 
        if char in SAFE_CONTROL_CHARS or not CONTROL_CHAR_PATTERN.match(char)
    )
    
    # Remove potentially dangerous file characters
    cleaned_title = re.sub(r'[<>:"|?*]', '', cleaned_title)
    
    # Trim whitespace
    cleaned_title = cleaned_title.strip()
    
    if not cleaned_title:
        return "Untitled Conversation"
    
    return cleaned_title


def validate_content(content: str) -> str:
    """
    Validate conversation content
    
    Args:
        content: The content to validate
        
    Returns:
        Validated content string
        
    Raises:
        ContentValidationError: If content is invalid
    """
    if not content:
        raise ContentValidationError("Content cannot be empty")
    
    # Check length
    if len(content) < MIN_CONTENT_LENGTH:
        raise ContentValidationError(
            f"Content too short: {len(content)} characters (min {MIN_CONTENT_LENGTH})"
        )
    
    if len(content) > MAX_CONTENT_LENGTH:
        raise ContentValidationError(
            f"Content too long: {len(content)} characters (max {MAX_CONTENT_LENGTH})"
        )
    
    # Remove null bytes for safety
    if NULL_BYTE_PATTERN.search(content):
        content = content.replace('\x00', '')
    
    return content


def validate_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Validate and parse date string
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Parsed datetime or None
        
    Raises:
        DateValidationError: If date format is invalid
    """
    if not date_str:
        return None
    
    try:
        # Handle common ISO formats
        if 'Z' in date_str:
            date_str = date_str.replace('Z', '+00:00')
        
        # Parse the date
        parsed_date = datetime.fromisoformat(date_str)
        
        # Sanity check - not too far in future or past
        now = datetime.now(parsed_date.tzinfo)
        years_diff = abs((parsed_date - now).days / 365)
        
        if years_diff > 100:
            raise DateValidationError(
                f"Date is unrealistic: {years_diff:.0f} years from now"
            )
        
        return parsed_date
        
    except (ValueError, TypeError) as e:
        raise DateValidationError(f"Invalid date format: {str(e)}")


def validate_search_query(query: str) -> str:
    """
    Validate search query
    
    Args:
        query: The search query to validate
        
    Returns:
        Sanitized query string
        
    Raises:
        QueryValidationError: If query is invalid
    """
    if not query:
        raise QueryValidationError("Query cannot be empty")
    
    # Check length
    if len(query) > MAX_QUERY_LENGTH:
        raise QueryValidationError(
            f"Query too long: {len(query)} characters (max {MAX_QUERY_LENGTH})"
        )
    
    # Remove null bytes
    if NULL_BYTE_PATTERN.search(query):
        raise QueryValidationError("Query contains null bytes")
    
    # Remove dangerous regex characters that could cause ReDoS
    # But keep basic search characters like spaces, letters, numbers
    query = re.sub(r'[<>\\]', '', query)
    
    # Trim whitespace
    query = query.strip()
    
    if not query:
        raise QueryValidationError("Query cannot be empty after sanitization")
    
    return query


def validate_limit(limit: int) -> int:
    """
    Validate search result limit
    
    Args:
        limit: The limit to validate
        
    Returns:
        Valid limit value
        
    Raises:
        ValidationError: If limit is invalid
    """
    if not isinstance(limit, int):
        raise ValidationError("Limit must be an integer")
    
    if limit < 1:
        return 1
    
    if limit > 100:
        return 100
    
    return limit