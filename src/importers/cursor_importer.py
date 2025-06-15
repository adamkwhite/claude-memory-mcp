#!/usr/bin/env python3
"""
Cursor AI conversation importer for Universal Memory MCP.

Handles Cursor AI session export format and converts to universal conversation format.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_importer import BaseImporter, ImportResult

logger = logging.getLogger(__name__)


class CursorImporter(BaseImporter):
    """Importer for Cursor AI session exports."""
    
    def __init__(self, storage_path: Path):
        super().__init__(storage_path, "cursor")
        self.logger = logging.getLogger(f"{__name__}.CursorImporter")
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file formats."""
        return [".json"]
    
    def import_file(self, file_path: Path) -> ImportResult:
        """
        Import conversations from a Cursor AI session export file.
        
        Cursor exports contain session-based interactions with code context.
        """
        try:
            if not file_path.exists():
                return ImportResult(
                    success=False,
                    conversations_imported=0,
                    conversations_failed=1,
                    errors=[f"File not found: {file_path}"],
                    imported_ids=[],
                    metadata={}
                )
            
            # Load and validate Cursor export file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not self._validate_cursor_format(data):
                return ImportResult(
                    success=False,
                    conversations_imported=0,
                    conversations_failed=1,
                    errors=["File is not a valid Cursor AI export format"],
                    imported_ids=[],
                    metadata={}
                )
            
            # Process the session as a single conversation
            try:
                # Parse the session into universal format
                universal_conv = self.parse_conversation(data)
                
                if self._validate_conversation(universal_conv):
                    # Save the conversation
                    self._save_conversation(universal_conv)
                    
                    return ImportResult(
                        success=True,
                        conversations_imported=1,
                        conversations_failed=0,
                        errors=[],
                        imported_ids=[universal_conv["id"]],
                        metadata={
                            "source_file": str(file_path),
                            "session_id": data.get("session_id", "unknown"),
                            "workspace": data.get("workspace", "unknown"),
                            "platform": "cursor",
                            "import_format": "cursor_session"
                        }
                    )
                else:
                    return ImportResult(
                        success=False,
                        conversations_imported=0,
                        conversations_failed=1,
                        errors=["Invalid conversation format after parsing"],
                        imported_ids=[],
                        metadata={}
                    )
                    
            except Exception as e:
                error_msg = f"Failed to process Cursor session: {str(e)}"
                self.logger.error(error_msg)
                return ImportResult(
                    success=False,
                    conversations_imported=0,
                    conversations_failed=1,
                    errors=[error_msg],
                    imported_ids=[],
                    metadata={}
                )
            
        except json.JSONDecodeError as e:
            return ImportResult(
                success=False,
                conversations_imported=0,
                conversations_failed=1,
                errors=[f"Invalid JSON format: {str(e)}"],
                imported_ids=[],
                metadata={}
            )
        except Exception as e:
            return ImportResult(
                success=False,
                conversations_imported=0,
                conversations_failed=1,
                errors=[f"Import failed: {str(e)}"],
                imported_ids=[],
                metadata={}
            )
    
    def parse_conversation(self, raw_data: Any) -> Dict[str, Any]:
        """
        Parse raw Cursor session data into universal format.
        
        Cursor format:
        {
            "session_id": "session-uuid",
            "workspace": "/path/to/project",
            "timestamp": "2025-01-01T12:00:00",
            "model": "claude-3.5-sonnet",
            "interactions": [
                {
                    "type": "user_input",
                    "content": "Fix this bug",
                    "files": ["src/main.py"],
                    "timestamp": "2025-01-01T12:00:00"
                },
                {
                    "type": "ai_response", 
                    "content": "Here's the fix...",
                    "changes": [{"file": "src/main.py", "diff": "..."}],
                    "timestamp": "2025-01-01T12:00:30"
                }
            ]
        }
        """
        if not isinstance(raw_data, dict):
            raise ValueError("Cursor session data must be a dictionary")
        
        # Extract basic session information
        session_id = raw_data.get("session_id", "")
        workspace = raw_data.get("workspace", "")
        model = raw_data.get("model", "cursor-ai")
        session_timestamp = raw_data.get("timestamp", "")
        
        # Parse session start time
        date = self._parse_timestamp(session_timestamp) if session_timestamp else datetime.now()
        
        # Generate title from workspace and session info
        workspace_name = Path(workspace).name if workspace else "Unknown Project"
        title = f"Cursor Session: {workspace_name}"
        
        # Process interactions
        interactions = raw_data.get("interactions", [])
        messages, full_content = self._process_interactions(interactions, workspace, model, session_id, date)
        
        # Create session context
        session_context = {
            "workspace": workspace,
            "workspace_name": workspace_name,
            "session_id": session_id,
            "model": model,
            "interaction_count": len(messages)
        }
        
        # Create universal conversation
        return self.create_universal_conversation(
            platform_id=session_id,
            title=title,
            content=full_content,
            messages=messages,
            date=date,
            model=model,
            session_context=session_context,
            metadata={
                "original_session_id": session_id,
                "workspace_path": workspace,
                "session_timestamp": session_timestamp,
                "interaction_count": len(interactions),
                "files_involved": self._extract_files_from_interactions(interactions)
            }
        )
    
    def _process_interactions(self, interactions: List[Any], workspace: str, model: str, session_id: str, date: datetime) -> tuple:
        """Process interactions and return messages and content."""
        messages = []
        content_parts = []
        
        # Add session header to content
        content_parts.append("# Cursor AI Session")
        content_parts.append(f"**Workspace**: {workspace}")
        content_parts.append(f"**Model**: {model}")
        content_parts.append(f"**Session ID**: {session_id}")
        content_parts.append("")
        
        for interaction in interactions:
            if not isinstance(interaction, dict):
                continue
            
            interaction_type = interaction.get("type", "unknown")
            content = interaction.get("content", "")
            timestamp_str = interaction.get("timestamp", "")
            
            # Skip empty interactions
            if not content or not content.strip():
                continue
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str) if timestamp_str else date
            
            # Determine role based on interaction type
            if interaction_type == "user_input":
                role = "user"
                role_display = "**Human**"
            elif interaction_type == "ai_response":
                role = "assistant"
                role_display = "**Cursor AI**"
            else:
                role = "system"
                role_display = f"**{interaction_type.title()}**"
            
            # Create message metadata
            metadata = {
                "interaction_type": interaction_type,
                "platform": "cursor"
            }
            
            # Add file context if available
            files = interaction.get("files", [])
            if files:
                metadata["files"] = files
                file_context = f"\n*Files: {', '.join(files)}*"
                content += file_context
            
            # Add code changes if available
            changes = interaction.get("changes", [])
            if changes:
                metadata["changes"] = changes
                change_summary = f"\n*{len(changes)} file(s) modified*"
                content += change_summary
            
            # Create standardized message
            message = self._create_message(
                role=role,
                content=content,
                timestamp=timestamp,
                metadata=metadata
            )
            messages.append(message)
            
            # Add to content string
            content_parts.append(f"{role_display}: {content}")
        
        # Combine all interactions into content string
        full_content = "\n\n".join(content_parts)
        return messages, full_content

    def _validate_cursor_format(self, data: Any) -> bool:
        """Validate that data is in Cursor AI session format."""
        if not isinstance(data, dict):
            return False
        
        # Look for Cursor-specific indicators
        cursor_indicators = ["session_id", "workspace", "interactions"]
        
        # Must have at least 2 of the key indicators
        indicator_count = sum(1 for key in cursor_indicators if key in data)
        if indicator_count < 2:
            return False
        
        # Check interactions structure if present
        if "interactions" in data:
            interactions = data["interactions"]
            if not isinstance(interactions, list):
                return False
            
            # Validate interaction structure
            if interactions:
                sample_interaction = interactions[0]
                if not isinstance(sample_interaction, dict):
                    return False
                
                # Should have type and content
                if "type" not in sample_interaction:
                    return False
        
        return True
    
    def _extract_files_from_interactions(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """Extract all files mentioned in interactions."""
        files = set()
        
        for interaction in interactions:
            # Files from user input
            if "files" in interaction:
                files.update(interaction["files"])
            
            # Files from code changes
            if "changes" in interaction:
                for change in interaction["changes"]:
                    if "file" in change:
                        files.add(change["file"])
        
        return sorted(list(files))
    
    def _save_conversation(self, conversation: Dict[str, Any]) -> Path:
        """Save a conversation to the storage directory."""
        # Create date-based subdirectory
        date = datetime.fromisoformat(conversation["date"].replace('Z', '+00:00'))
        year_folder = self.storage_path / str(date.year)
        month_folder = year_folder / f"{date.month:02d}-{date.strftime('%B').lower()}"
        month_folder.mkdir(parents=True, exist_ok=True)
        
        # Save conversation file
        filename = f"{conversation['id']}.json"
        file_path = month_folder / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
        
        self.logger.info("Saved Cursor session to: %s", file_path)
        return file_path
    
    def _extract_topics(self, content: str) -> List[str]:
        """Override base topic extraction for Cursor-specific patterns."""
        topics = super()._extract_topics(content)
        
        # Add Cursor-specific topic indicators
        content_lower = content.lower()
        
        # Cursor-specific terms
        cursor_topics = [
            "cursor", "ide", "code editor", "ai coding", "code assistant",
            "refactoring", "debugging", "code generation", "pair programming"
        ]
        
        for topic in cursor_topics:
            if topic in content_lower and topic not in topics:
                topics.append(topic)
        
        # Extract programming language topics from file extensions
        file_extensions = {
            ".py": "python",
            ".js": "javascript", 
            ".ts": "typescript",
            ".jsx": "react",
            ".tsx": "react typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "golang",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin"
        }
        
        for ext, lang in file_extensions.items():
            if ext in content_lower and lang not in topics:
                topics.append(lang)
        
        # Always include platform identifier
        if "cursor" not in topics:
            topics.append("cursor")
        
        return topics[:10]  # Limit to 10 topics


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        storage_path = Path("./test_imports")
        
        importer = CursorImporter(storage_path)
        result = importer.import_file(file_path)
        
        print(f"Import Result:")
        print(f"  Success: {result.success}")
        print(f"  Imported: {result.conversations_imported}")
        print(f"  Failed: {result.conversations_failed}")
        print(f"  Success Rate: {result.success_rate:.2%}")
        
        if result.errors:
            print(f"  Errors: {result.errors}")
        
        if result.imported_ids:
            print(f"  Imported IDs: {result.imported_ids}")
        
        print(f"  Metadata: {result.metadata}")
    else:
        print("Usage: python cursor_importer.py <cursor_session.json>")