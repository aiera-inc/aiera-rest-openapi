#!/usr/bin/env python3

import os
import json
from typing import Dict, Any
from mangum import Mangum
from server import mcp

# Configure the MCP server for Lambda deployment
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for the Aiera MCP server."""
    
    # Ensure required environment variables are set
    if not os.getenv("AIERA_API_KEY"):
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "AIERA_API_KEY environment variable is required"}),
            "headers": {"Content-Type": "application/json"}
        }
    
    # Create the ASGI application from FastMCP
    app = mcp.sse_app()
    
    # Use Mangum to adapt the ASGI app for Lambda
    handler = Mangum(app, lifespan="off")
    
    return handler(event, context)

# For local testing with AWS Lambda Runtime Interface Emulator
if __name__ == "__main__":
    # This allows running the handler locally for testing
    test_event = {
        "httpMethod": "GET",
        "path": "/",
        "headers": {"Content-Type": "application/json"},
        "body": None
    }
    
    class MockContext:
        def __init__(self):
            self.function_name = "test-function"
            self.function_version = "1"
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
            self.memory_limit_in_mb = 512
            self.remaining_time_in_millis = 30000
            self.log_group_name = "/aws/lambda/test-function"
            self.log_stream_name = "2021/01/01/[1]abcdef123456789"
            self.aws_request_id = "abcdef123456789"
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))