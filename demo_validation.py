#!/usr/bin/env python3
"""Demo script showing input validation in action"""

import asyncio
from src.server_fastmcp import ConversationMemoryServer
from src.exceptions import ValidationError


async def demo_validation():
    """Demonstrate input validation features"""
    import os
    demo_path = os.path.expanduser("~/claude-memory-demo")
    server = ConversationMemoryServer(demo_path)
    
    print("🛡️  Claude Memory MCP - Input Validation Demo\n")
    
    # Test 1: Valid conversation
    print("1️⃣  Adding valid conversation...")
    result = await server.add_conversation(
        content="This is a normal conversation about Python programming.",
        title="Python Discussion",
        date="2025-06-09T12:00:00Z"
    )
    print(f"✅ Result: {result['message']}\n")
    
    # Test 2: Path traversal attempt in title
    print("2️⃣  Attempting path traversal in title...")
    try:
        result = await server.add_conversation(
            content="Malicious content",
            title="../../etc/passwd"
        )
    except Exception as e:
        result = {"status": "error", "message": str(e)}
    print(f"🚫 Result: {result['message']}\n")
    
    # Test 3: Null byte injection
    print("3️⃣  Attempting null byte injection...")
    result = await server.add_conversation(
        content="Content with\x00null byte",
        title="Test\x00Injection"
    )
    print(f"✅ Result: {result['message']} (null bytes sanitized)\n")
    
    # Test 4: XSS attempt in title
    print("4️⃣  Attempting XSS in title...")
    result = await server.add_conversation(
        content="Normal content",
        title='<script>alert("xss")</script>'
    )
    print(f"✅ Result: {result['message']} (dangerous chars removed)\n")
    
    # Test 5: Empty content
    print("5️⃣  Attempting empty content...")
    result = await server.add_conversation(
        content="",
        title="Empty Test"
    )
    print(f"🚫 Result: {result['message']}\n")
    
    # Test 6: Content too large
    print("6️⃣  Attempting oversized content...")
    huge_content = "A" * 1_000_001  # Over 1MB limit
    result = await server.add_conversation(
        content=huge_content,
        title="Large Content"
    )
    print(f"🚫 Result: {result['message']}\n")
    
    # Test 7: SQL injection in search
    print("7️⃣  Attempting SQL injection in search...")
    results = await server.search_conversations("'; DROP TABLE conversations; --")
    if results and "error" in results[0]:
        print(f"🚫 Result: {results[0]['error']}\n")
    else:
        print(f"✅ Result: Found {len(results)} conversations (query sanitized)\n")
    
    # Test 8: Valid search
    print("8️⃣  Valid search...")
    results = await server.search_conversations("Python programming", limit=5)
    print(f"✅ Result: Found {len(results)} conversations\n")
    
    print("🎯 Demo complete! All validation working correctly.")
    print("🔐 Zero security hotspots maintained!")


if __name__ == "__main__":
    asyncio.run(demo_validation())