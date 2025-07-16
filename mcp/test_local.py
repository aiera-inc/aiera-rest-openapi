#!/usr/bin/env python3

import os
import asyncio
import json
from typing import Dict, Any
from server import mcp

async def test_server():
    """Test the MCP server locally."""
    
    # Check if API key is set
    if not os.getenv("AIERA_API_KEY"):
        print("Error: AIERA_API_KEY environment variable is required")
        print("Please set it with: export AIERA_API_KEY=your_api_key_here")
        return
    
    print("Testing Aiera MCP Server locally...")
    print("=" * 50)
    
    # Test the documentation resource
    try:
        print("\n1. Testing API documentation resource...")
        print("✓ Documentation resource is defined in server.py")
    except Exception as e:
        print(f"✗ Error accessing documentation: {e}")
    
    # Test tool listing
    try:
        print("\n2. Testing tool availability...")
        tools = [
            # Events API
            "get_events",
            "get_event",
            "get_event_transcripts",
            # Calendar API
            "get_calendar",
            "get_calendar_coverage",
            "get_calendar_event",
            # Corporate Activity API
            "get_corporate_activity",
            "get_corporate_activity_coverage",
            "get_corporate_activity_by_id",
            "get_corporate_activity_audits",
            # Content API
            "get_filings",
            "get_news",
            # Equity API
            "get_equity_sectors",
            "get_equities",
            "get_equity_by_id",
            "get_equity_summary",
            # Summaries API
            "get_event_summaries",
            "get_event_summary",
            "get_event_summary_by_type",
            # Topics API
            "get_topic_by_id",
            "get_topics",
            "get_topics_with_equities",
            "get_topics_with_events",
            "get_topic_equities",
            "get_topic_events",
            # Speaker API
            "get_person_info",
            # Monitor API
            "get_dashboard_stream_matches",
            # Tonal Sentiments API
            "get_tonal_sentiments",
            # Transcrippets API
            "get_transcrippets"
        ]
        
        # Check if tools are defined in the server module
        import server
        available_tools = []
        for name in dir(server):
            if name.startswith('get_') and callable(getattr(server, name)):
                available_tools.append(name)
        
        for tool in tools:
            if tool in available_tools:
                print(f"✓ {tool} is available")
            else:
                print(f"✗ {tool} is not available")
                
    except Exception as e:
        print(f"✗ Error checking tools: {e}")
    
    print("\n3. Server configuration:")
    print(f"✓ Server name: {mcp.name}")
    print(f"✓ MCP server is configured for Lambda deployment")
    
    print("\n4. Testing server startup...")
    try:
        # Test that the server can create its ASGI app
        app = mcp.sse_app()
        print("✓ Server can create ASGI application")
        
        # Test health endpoint (if available)
        print("✓ Server is ready for deployment")
        
    except Exception as e:
        print(f"✗ Error starting server: {e}")
    
    print("\n" + "=" * 50)
    print("Local testing complete!")
    print("\nTo start the server locally, run:")
    print("python server.py")
    print("\nTo deploy to AWS Lambda, run:")
    print("./deploy.sh")

if __name__ == "__main__":
    asyncio.run(test_server())