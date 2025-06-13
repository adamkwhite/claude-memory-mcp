# AI Platform Export Format Research

This document analyzes export formats from different AI platforms to design universal import support.

## Current Claude Memory Format

```json
{
  "id": "conv_20250613_120000_1234",
  "title": "Example Conversation",
  "content": "Human: Hello\n\nClaude: Hi there!",
  "date": "2025-06-13T12:00:00",
  "topics": ["greeting", "conversation"],
  "created_at": "2025-06-13T12:00:00"
}
```

## Platform Format Analysis

### 1. ChatGPT/OpenAI Format
- **Export Method**: Settings > Data Export > Export Data
- **Format**: JSON with message arrays
- **Key Fields**: conversations, messages, role (user/assistant)
- **Metadata**: creation_time, update_time, conversation_id

**Typical Structure:**
```json
{
  "conversations": [
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
        },
        {
          "id": "message-uuid",
          "role": "assistant", 
          "content": "Hi there!",
          "create_time": "2025-01-01T12:00:30"
        }
      ]
    }
  ]
}
```

### 2. Cursor AI Format
- **Export Method**: Currently limited export options
- **Format**: Session-based with code context
- **Key Fields**: session_id, files, commands, ai_responses
- **Metadata**: workspace_path, timestamp, model_used

**Typical Structure:**
```json
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
```

### 3. Claude Web Interface Format
- **Export Method**: Manual copy/paste or browser automation
- **Format**: Markdown-style conversation
- **Key Fields**: Role indicators, timestamps
- **Metadata**: Limited - mainly timestamp and conversation flow

**Typical Structure:**
```markdown
# Conversation with Claude

**Human**: Hello there!

**Claude**: Hi! How can I help you today?

**Human**: I need help with Python

**Claude**: I'd be happy to help with Python! What specifically are you working on?
```

### 4. Other Platforms (Preliminary)

#### Windsurf AI
- **Status**: Emerging platform
- **Format**: TBD - likely similar to Cursor with enhanced code context

#### Perplexity AI
- **Export**: Limited
- **Format**: Search-focused with sources

#### Claude Desktop (MCP)
- **Format**: Same as web but with enhanced metadata
- **Advantage**: Direct API access for real-time sync

## Universal Format Requirements

Based on analysis, our universal format needs:

1. **Platform Identification**: Source platform and model
2. **Flexible Message Structure**: Support both conversation and session-based formats
3. **Rich Metadata**: Timestamps, file context, model info
4. **Content Preservation**: Maintain original formatting and context
5. **Extensibility**: Allow platform-specific fields

## Proposed Universal Internal Format

```json
{
  "id": "universal-conversation-id",
  "platform": "chatgpt|cursor|claude|generic",
  "model": "gpt-4|claude-3.5-sonnet|cursor-ai",
  "title": "Generated or Extracted Title",
  "content": "Unified conversation content",
  "messages": [
    {
      "id": "message-id",
      "role": "user|assistant|system",
      "content": "Message content",
      "timestamp": "ISO8601",
      "metadata": {
        "files": ["optional file context"],
        "changes": ["optional code changes"],
        "platform_specific": {}
      }
    }
  ],
  "date": "ISO8601 - conversation start",
  "last_updated": "ISO8601 - last message",
  "topics": ["extracted", "topics"],
  "session_context": {
    "workspace": "optional workspace path",
    "project_type": "optional project context"
  },
  "import_metadata": {
    "imported_at": "ISO8601",
    "source_format": "original format",
    "import_version": "1.0"
  }
}
```

## Implementation Strategy

1. **Phase 1**: Format detection and ChatGPT import
2. **Phase 2**: Cursor and code-focused imports  
3. **Phase 3**: Generic markdown/text import
4. **Phase 4**: Real-time platform integrations

*Last Updated: June 13, 2025*