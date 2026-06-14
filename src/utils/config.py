import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """Application settings managed by Pydantic."""
    
    app_name: str = "ExplainInk AI"
    log_level: str = "INFO"
    gemini_api_key: str = ""
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    temp_dir: Path = base_dir / "temp"
    output_dir: Path = base_dir / "output"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()
