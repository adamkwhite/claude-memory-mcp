#!/usr/bin/env python3
"""
Test script for Claude Memory MCP Server

Run this to verify your server installation and basic functionality.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from server_fastmcp import ConversationMemoryServer

async def test_server():
    """Test basic server functionality"""
    print("🧪 Testing Claude Memory MCP Server...")
    
    # Initialize server with test directory
    test_path = Path("~/claude-memory-test").expanduser()
    server = ConversationMemoryServer(str(test_path))
    
    print(f"📁 Using test directory: {test_path}")
    
    # Test 1: Add a conversation
    print("\n1️⃣ Testing conversation addition...")
    test_content = """
    # Test Conversation
    
    **Human**: How do I set up a Python MCP server?
    
    **Claude**: To set up a Python MCP server, you need to:
    1. Install the mcp package
    2. Create a server.py file with the MCP server code
    3. Define your tools and handlers
    4. Configure Claude Desktop to use your server
    
    The key is to implement the @app.list_tools() and @app.call_tool() decorators properly.
    """
    
    result = await server.add_conversation(
        content=test_content,
        title="MCP Server Setup Discussion",
        date="2025-01-15T10:30:00"
    )
    
    print(f"✅ Add conversation result: {result['status']}")
    if result['status'] == 'success':
        print(f"   📄 File: {result['file_path']}")
        print(f"   🏷️  Topics: {result['topics']}")
    else:
        print(f"❌ Error: {result['message']}")
        return False
    
    # Test 2: Search conversations
    print("\n2️⃣ Testing conversation search...")
    search_results = await server.search_conversations("MCP server", limit=3)
    
    if search_results and not any("error" in result for result in search_results):
        print(f"✅ Found {len(search_results)} conversations")
        for i, result in enumerate(search_results, 1):
            print(f"   {i}. {result['title']} (score: {result['score']})")
    else:
        print(f"❌ Search failed or no results found")
        return False
    
    # Test 3: Verify file structure
    print("\n3️⃣ Testing file structure...")
    expected_files = [
        test_path / "conversations" / "index.json",
        test_path / "conversations" / "topics.json",
        test_path / "summaries" / "weekly"
    ]
    
    all_exist = True
    for file_path in expected_files:
        if file_path.exists():
            print(f"   ✅ {file_path.name}")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_exist = False
    
    # Test 4: Check index content
    print("\n4️⃣ Testing index integrity...")
    try:
        with open(test_path / "conversations" / "index.json", 'r') as f:
            index_data = json.load(f)
        
        conv_count = len(index_data.get("conversations", []))
        print(f"   ✅ Index contains {conv_count} conversations")
        
        with open(test_path / "conversations" / "topics.json", 'r') as f:
            topics_data = json.load(f)
        
        topic_count = len(topics_data.get("topics", {}))
        print(f"   ✅ Topics index contains {topic_count} topics")
        
    except Exception as e:
        print(f"   ❌ Index file error: {e}")
        all_exist = False
    
    # Summary
    print("\n📊 Test Summary:")
    if all_exist and result['status'] == 'success' and search_results:
        print("✅ All tests passed! Your MCP server is working correctly.")
        print(f"\n🗂️  Test files created in: {test_path}")
        print("   You can now configure Claude Desktop to use this server.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

def test_imports():
    """Test that all required imports are available"""
    print("📦 Testing imports...")
    
    try:
        import mcp.types
        print("   ✅ mcp.types")
    except ImportError:
        print("   ❌ mcp.types - Install with: pip install mcp")
        return False
    
    try:
        import mcp.server
        print("   ✅ mcp.server")
    except ImportError:
        print("   ❌ mcp.server - Install with: pip install mcp")
        return False
    
    try:
        import mcp.server.stdio
        print("   ✅ mcp.server.stdio")
    except ImportError:
        print("   ❌ mcp.server.stdio - Install with: pip install mcp")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Claude Memory MCP Server Test Suite")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed. Please install requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Test server functionality
    success = await test_server()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Copy server files to Ubuntu/WSL: ~/claude-memory-mcp/")
        print("2. Configure Claude Desktop with the MCP server")
        print("3. Start using /mem commands in your conversations")
        sys.exit(0)
    else:
        print("\n💥 Tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
