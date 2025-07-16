#!/usr/bin/env python3

import os
from typing import Optional, Dict, Any

class Config:
    """Configuration class for Aiera MCP Server."""
    
    # Aiera API Configuration
    AIERA_BASE_URL: str = "https://premium.aiera.com/api"
    AIERA_API_KEY: Optional[str] = os.getenv("AIERA_API_KEY")
    
    # Server Configuration
    SERVER_NAME: str = "Aiera Financial Data API"
    SERVER_VERSION: str = "1.0.0"
    
    # Lambda Configuration
    LAMBDA_MEMORY_SIZE: int = int(os.getenv("LAMBDA_MEMORY_SIZE", "512"))
    LAMBDA_TIMEOUT: int = int(os.getenv("LAMBDA_TIMEOUT", "30"))
    
    # Deployment Configuration
    STAGE: str = os.getenv("STAGE", "dev")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # HTTP Client Configuration
    HTTP_TIMEOUT: float = 30.0
    HTTP_RETRIES: int = 3
    
    # Security Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list = [
        "Content-Type",
        "X-Amz-Date", 
        "Authorization",
        "X-Api-Key",
        "X-Amz-Security-Token"
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Validation Configuration
    MAX_QUERY_LENGTH: int = 1000
    MAX_RESULTS_PER_REQUEST: int = 1000
    DEFAULT_LIMIT: int = 100
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if not cls.AIERA_API_KEY:
            raise ValueError("AIERA_API_KEY environment variable is required")
        
        if cls.STAGE not in ["dev", "staging", "prod"]:
            raise ValueError("STAGE must be one of: dev, staging, prod")
        
        if cls.LAMBDA_MEMORY_SIZE < 128 or cls.LAMBDA_MEMORY_SIZE > 10240:
            raise ValueError("LAMBDA_MEMORY_SIZE must be between 128 and 10240 MB")
        
        if cls.LAMBDA_TIMEOUT < 1 or cls.LAMBDA_TIMEOUT > 900:
            raise ValueError("LAMBDA_TIMEOUT must be between 1 and 900 seconds")
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Content-Type": "application/json",
            "User-Agent": f"{cls.SERVER_NAME}/{cls.SERVER_VERSION}",
            "X-API-KEY": cls.AIERA_API_KEY or ""
        }
    
    @classmethod
    def get_stack_name(cls) -> str:
        """Get CloudFormation stack name."""
        return f"aiera-mcp-server-{cls.STAGE}"
    
    @classmethod
    def get_function_name(cls) -> str:
        """Get Lambda function name."""
        return f"aiera-mcp-server-{cls.STAGE}"
    
    @classmethod
    def get_api_name(cls) -> str:
        """Get API Gateway name."""
        return f"aiera-mcp-api-{cls.STAGE}"
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "server_name": cls.SERVER_NAME,
            "server_version": cls.SERVER_VERSION,
            "stage": cls.STAGE,
            "aws_region": cls.AWS_REGION,
            "lambda_memory_size": cls.LAMBDA_MEMORY_SIZE,
            "lambda_timeout": cls.LAMBDA_TIMEOUT,
            "log_level": cls.LOG_LEVEL,
            "debug": cls.DEBUG,
            "aiera_base_url": cls.AIERA_BASE_URL,
            "has_api_key": bool(cls.AIERA_API_KEY)
        }

# Global configuration instance
config = Config()

# Validate configuration on import
if os.getenv("VALIDATE_CONFIG", "true").lower() == "true":
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        if config.STAGE == "prod":
            raise  # Fail fast in production
        else:
            print("Continuing with incomplete configuration for development...")