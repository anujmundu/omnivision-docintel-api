"""
Application Configuration and Environment Settings.
Supports pydantic-settings with fallback to standard Pydantic.
"""

from typing import List

try:
    from pydantic_settings import BaseSettings
    class BaseConfig(BaseSettings):
        pass
except ImportError:
    from pydantic import BaseModel
    class BaseConfig(BaseModel):
        pass


class Settings(BaseConfig):
    PROJECT_NAME: str = "OmniVision-DocIntel API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = "Enterprise Document Intelligence & Multimodal Vision Microservice"
    
    # Security & Access
    API_KEY: str = "demo-omni-key-2026"
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Vision Thresholds
    BLUR_THRESHOLD: float = 100.0
    MAX_FILE_SIZE_MB: int = 15


settings = Settings()
