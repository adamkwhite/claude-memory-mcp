#!/usr/bin/env python3
"""
ChatGPT conversation importer for Universal Memory MCP.

Handles OpenAI ChatGPT export format and converts to universal conversation format.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_importer import BaseImporter, ImportResult

logger = logging.getLogger(__name__)


class ChatGPTImporter(BaseImporter):
    """Importer for ChatGPT conversation exports."""
    
    def __init__(self, storage_path: Path):
        super().__init__(storage_path, "chatgpt")
        self.logger = logging.getLogger(f"{__name__}.ChatGPTImporter")
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file formats."""
        return [".json"]
    
    def import_file(self, file_path: Path) -> ImportResult:
        """
        Import conversations from a ChatGPT export file.
        
        ChatGPT exports contain a 'conversations' array with message-based structure.
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
            
            # Load and validate ChatGPT export file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not self._validate_chatgpt_format(data):
                return ImportResult(
                    success=False,
                    conversations_imported=0,
                    conversations_failed=1,
                    errors=["File is not a valid ChatGPT export format"],
                    imported_ids=[],
                    metadata={}
                )
            
            # Process each conversation
            conversations = data.get("conversations", [])
            return self._process_conversations(conversations, file_path)
            
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
    
    def _process_conversations(self, conversations: List[Any], file_path: Path) -> ImportResult:
        """Process list of conversations and return import result."""
        imported_count = 0
        failed_count = 0
        errors = []
        imported_ids = []
        
        for conversation in conversations:
            try:
                # Parse the conversation into universal format
                universal_conv = self.parse_conversation(conversation)
                
                if self._validate_conversation(universal_conv):
                    # Save the conversation
                    self._save_conversation(universal_conv)
                    imported_ids.append(universal_conv["id"])
                    imported_count += 1
                    self.logger.info("Imported ChatGPT conversation: %s", universal_conv['id'])
                else:
                    failed_count += 1
                    errors.append(f"Invalid conversation format for ID: {conversation.get('id', 'unknown')}")
                    
            except Exception as e:
                failed_count += 1
                conv_id = conversation.get("id", "unknown")
                error_msg = f"Failed to process conversation {conv_id}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        return ImportResult(
            success=imported_count > 0,
            conversations_imported=imported_count,
            conversations_failed=failed_count,
            errors=errors,
            imported_ids=imported_ids,
            metadata={
                "source_file": str(file_path),
                "total_conversations_in_file": len(conversations),
                "platform": "chatgpt",
                "import_format": "openai_export"
            }
        )

    def parse_conversation(self, raw_data: Any) -> Dict[str, Any]:
        """
        Parse raw ChatGPT conversation data into universal format.
        
        ChatGPT format:
        {
            "id": "conversation-uuid",
            "title": "Conversation Title", 
            "create_time": "2025-01-01T12:00:00",
            "update_time": "2025-01-01T12:30:00",
            "messages": [
                {
                    "id": "message-uuid",
                    "role": "user",
                    "content": "Hello",
                    "create_time": "2025-01-01T12:00:00"
                }
            ]
        }
        """
        if not isinstance(raw_data, dict):
            raise ValueError("ChatGPT conversation data must be a dictionary")
        
        # Extract basic information
        platform_id = raw_data.get("id", "")
        title = raw_data.get("title", "Untitled ChatGPT Conversation")
        
        # Parse timestamps
        create_time_str = raw_data.get("create_time", "")
        update_time_str = raw_data.get("update_time", "")
        
        date = self._parse_timestamp(create_time_str) if create_time_str else datetime.now()
        
        # Process messages
        raw_messages = raw_data.get("messages", [])
        messages = []
        content_parts = []
        
        for msg in raw_messages:
            if not isinstance(msg, dict):
                continue
            
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            msg_time_str = msg.get("create_time", "")
            
            # Skip empty messages
            if not content or not content.strip():
                continue
            
            # Create standardized message
            timestamp = self._parse_timestamp(msg_time_str) if msg_time_str else date
            
            message = self._create_message(
                role=role,
                content=content,
                timestamp=timestamp,
                message_id=msg.get("id"),
                metadata={
                    "original_create_time": msg_time_str,
                    "platform": "chatgpt"
                }
            )
            messages.append(message)
            
            # Add to content string for full conversation text
            role_display = "**Human**" if role == "user" else f"**{role.title()}**"
            content_parts.append(f"{role_display}: {content}")
        
        # Combine all messages into content string
        content = "\n\n".join(content_parts)
        
        # Extract model information if available
        model = self._extract_model_info(raw_data)
        
        # Create universal conversation
        return self.create_universal_conversation(
            platform_id=platform_id,
            title=title,
            content=content,
            messages=messages,
            date=date,
            model=model,
            session_context={
                "update_time": update_time_str,
                "original_platform": "chatgpt"
            },
            metadata={
                "original_id": platform_id,
                "original_create_time": create_time_str,
                "original_update_time": update_time_str,
                "message_count": len(messages)
            }
        )
    
    def _validate_chatgpt_format(self, data: Any) -> bool:
        """Validate that data is in ChatGPT export format."""
        if not isinstance(data, dict):
            return False
        
        # Must have conversations array
        if "conversations" not in data:
            return False
        
        conversations = data["conversations"]
        if not isinstance(conversations, list):
            return False
        
        # Check at least one conversation has required structure
        if conversations:
            sample_conv = conversations[0]
            if not isinstance(sample_conv, dict):
                return False
            
            # Should have messages array
            if "messages" not in sample_conv:
                return False
            
            messages = sample_conv["messages"]
            if not isinstance(messages, list):
                return False
            
            # Check message structure
            if messages:
                sample_msg = messages[0]
                if not isinstance(sample_msg, dict):
                    return False
                
                # Should have role and content
                if "role" not in sample_msg or "content" not in sample_msg:
                    return False
        
        return True
    
    def _extract_model_info(self, conversation_data: Dict[str, Any]) -> str:
        """Extract model information from conversation data."""
        # ChatGPT exports don't always include model info explicitly
        # We can infer from metadata or default to GPT-4
        
        # Check if there's model info in the conversation
        if "model" in conversation_data:
            return conversation_data["model"]
        
        # Check messages for model hints
        messages = conversation_data.get("messages", [])
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                # Look for model indicators in assistant responses
                content = msg.get("content", "").lower()
                if "gpt-4" in content:
                    return "gpt-4"
                elif "gpt-3.5" in content:
                    return "gpt-3.5-turbo"
        
        # Default assumption for ChatGPT exports
        return "gpt-4"
    
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
        
        self.logger.info(f"Saved conversation to: {file_path}")
        return file_path
    
    def _extract_topics(self, content: str) -> List[str]:
        """Override base topic extraction for ChatGPT-specific patterns."""
        topics = super()._extract_topics(content)
        
        # Add ChatGPT-specific topic indicators
        content_lower = content.lower()
        
        # ChatGPT-specific terms
        chatgpt_topics = [
            "openai", "gpt", "artificial intelligence", "language model",
            "prompt", "chatbot", "ai assistant", "machine learning"
        ]
        
        for topic in chatgpt_topics:
            if topic in content_lower and topic not in topics:
                topics.append(topic)
        
        # Always include platform identifier
        if "chatgpt" not in topics:
            topics.append("chatgpt")
        
        return topics[:10]  # Limit to 10 topics


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        storage_path = Path("./test_imports")
        
        importer = ChatGPTImporter(storage_path)
        result = importer.import_file(file_path)
        
        print(f"Import Result:")
        print(f"  Success: {result.success}")
        print(f"  Imported: {result.conversations_imported}")
        print(f"  Failed: {result.conversations_failed}")
        print(f"  Success Rate: {result.success_rate:.2%}")
        
        if result.errors:
            print(f"  Errors: {result.errors}")
        
        if result.imported_ids:
            print(f"  Imported IDs: {result.imported_ids[:3]}...")
    else:
        print("Usage: python chatgpt_importer.py <chatgpt_export.json>")