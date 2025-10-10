#!/usr/bin/env python3
"""
Claude Conversation Memory MCP Server (FastMCP Version)

This MCP server provides tools for managing and searching Claude conversation history.
Supports storing conversations locally and retrieving context for current sessions.
"""

from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

try:
    from .conversation_memory import ConversationMemoryServer as CoreMemoryServer
    from .logging_config import (
        get_logger,
        init_default_logging,
        log_function_call,
        log_security_event,
    )
except ImportError:
    # For direct imports during testing
    from conversation_memory import ConversationMemoryServer as CoreMemoryServer
    from logging_config import (
        get_logger,
        init_default_logging,
        log_function_call,
        log_security_event,
    )

# Constants
DEFAULT_PREVIEW_LENGTH = 500
DEFAULT_CONTENT_PREVIEW = 200
MAX_PREVIEW_LINES = 10
CONTEXT_LINES_BEFORE = 2
CONTEXT_LINES_AFTER = 3
DEFAULT_SEARCH_LIMIT = 5
MAX_RESULTS_DISPLAY = 10
UTC_OFFSET_REPLACEMENT = "+00:00"

COMMON_TECH_TERMS = [
    "python",
    "javascript",
    "react",
    "node",
    "aws",
    "docker",
    "kubernetes",
    "terraform",
    "mcp",
    "api",
    "database",
    "sql",
    "mongodb",
    "redis",
    "git",
    "github",
    "vscode",
    "linux",
    "ubuntu",
    "windows",
    "wsl",
    "authentication",
    "security",
    "testing",
    "deployment",
    "ci/cd",
]


class FastMCPConversationMemoryServer(CoreMemoryServer):
    """FastMCP-specific wrapper around the core ConversationMemoryServer."""

    def __init__(
        self, storage_path: str = "~/claude-memory", use_data_dir: bool = None
    ):
        # Initialize logging for FastMCP
        init_default_logging()
        self.fastmcp_logger = get_logger("claude_memory_mcp.server")

        log_function_call(
            "FastMCPConversationMemoryServer.__init__",
            storage_path=storage_path,
            use_data_dir=use_data_dir,
        )

        # Validate storage path for security
        storage_path_obj = Path(storage_path).expanduser().resolve()
        self._validate_storage_path(storage_path_obj)

        # Initialize the core memory server with SQLite enabled
        super().__init__(
            storage_path=storage_path, use_data_dir=use_data_dir, enable_sqlite=True
        )

        self.fastmcp_logger.info(
            f"FastMCP Server initialized with SQLite: {self.use_sqlite_search}"
        )

    def _validate_storage_path(self, storage_path: Path):
        """Validate storage path for security."""
        log_function_call("_validate_storage_path", storage_path=str(storage_path))

        # Ensure path doesn't contain traversal attempts
        if ".." in str(storage_path):
            log_security_event(
                "PATH_TRAVERSAL_ATTEMPT",
                f"Storage path contains '..' traversal: {storage_path}",
                "ERROR",
            )
            raise ValueError("Storage path cannot contain '..' for security reasons")

        # Ensure path is within user's home directory or explicit allowed paths
        home = Path.home().resolve()
        project_root = Path(__file__).parent.parent.resolve()

        # Allow paths in home directory or project directory (for testing)
        if not (
            str(storage_path).startswith(str(home))
            or str(storage_path).startswith(str(project_root))
        ):
            log_security_event(
                "PATH_OUTSIDE_HOME",
                f"Storage path outside allowed directories: {storage_path}",
                "ERROR",
            )
            raise ValueError(
                "Storage path must be within user's home directory or project directory"
            )

        self.fastmcp_logger.debug(f"Storage path validation passed: {storage_path}")


# Initialize FastMCP server and memory system
mcp = FastMCP("claude-memory")
memory_server = FastMCPConversationMemoryServer()


@mcp.tool()
async def search_conversations(query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> str:
    """Search through stored Claude conversations for relevant content"""
    results = await memory_server.search_conversations(query, limit)

    if not results:
        return f"No conversations found matching '{query}'"

    response = f"Found {len(results)} conversations matching '{query}':\n\n"
    for i, result in enumerate(results, 1):
        if "error" in result:
            response += f"Error: {result['error']}\n"
            continue

        response += f"**{i}. {result['title']}**\n"
        response += f"Date: {result['date']}\n"
        response += f"Topics: {', '.join(result['topics'])}\n"
        response += f"Relevance Score: {result['score']}\n"
        response += f"Preview:\n```\n{result['preview']}\n```\n\n"

    return response


@mcp.tool()
async def add_conversation(
    content: str, title: Optional[str] = None, date: Optional[str] = None
) -> str:
    """Add a new conversation to the memory system"""
    result = await memory_server.add_conversation(content, title, date)
    return f"Status: {result['status']}\n{result['message']}"


@mcp.tool()
async def generate_weekly_summary(week_offset: int = 0) -> str:
    """Generate a summary of conversations from the past week"""
    return await memory_server.generate_weekly_summary(week_offset)


@mcp.tool()
async def search_by_topic(topic: str, limit: int = 10) -> str:
    """Search conversations by a specific topic"""
    results = await memory_server.search_by_topic(topic, limit)

    if not results:
        return f"No conversations found for topic '{topic}'"

    response = f"Found {len(results)} conversations for topic '{topic}':\n\n"
    for i, result in enumerate(results, 1):
        if "error" in result:
            response += f"Error: {result['error']}\n"
        else:
            response += f"**{i}. {result.get('title', 'Untitled')}**\n"
            response += f"ID: {result['id']}\n"
            if "date" in result:
                response += f"Date: {result['date']}\n"
            if "preview" in result:
                response += f"Preview:\n```\n{result['preview']}\n```\n\n"

    return response


@mcp.tool()
async def get_search_stats() -> str:
    """Get search engine statistics and performance information"""
    stats = await memory_server.get_search_stats()

    response = "Search Engine Statistics:\n\n"
    response += f"• SQLite Available: {stats.get('sqlite_available', 'Unknown')}\n"
    response += f"• SQLite Enabled: {stats.get('sqlite_enabled', 'Unknown')}\n"
    response += f"• Current Engine: {stats.get('search_engine', 'Unknown')}\n"

    if "total_conversations" in stats:
        response += f"• Total Conversations: {stats['total_conversations']}\n"

    if "unique_topics" in stats:
        response += f"• Unique Topics: {stats['unique_topics']}\n"

    if "popular_topics" in stats:
        response += "\nPopular Topics:\n"
        for topic_info in stats["popular_topics"][:5]:
            response += (
                f"  - {topic_info['topic']}: {topic_info['count']} conversations\n"
            )

    if "sqlite_error" in stats:
        response += f"\nSQLite Error: {stats['sqlite_error']}\n"

    return response


@mcp.tool()
async def migrate_to_sqlite() -> str:
    """Migrate existing JSON conversations to SQLite database for better search performance"""
    result = await memory_server.migrate_to_sqlite()

    if "error" in result:
        return f"Migration failed: {result['error']}"

    response = "Migration Results:\n\n"
    response += f"• Total Found: {result.get('total_found', 0)}\n"
    response += f"• Successfully Migrated: {result.get('successfully_migrated', 0)}\n"
    response += f"• Failed Migrations: {result.get('failed_migrations', 0)}\n"
    response += f"• Skipped: {result.get('skipped', 0)}\n"

    if result.get("successfully_migrated", 0) > 0:
        response += "\n✅ Migration completed successfully!"
        response += "\nSearch performance should now be significantly improved."
    else:
        response += "\n⚠️ No conversations were migrated."

    return response


if __name__ == "__main__":
    mcp.run()
