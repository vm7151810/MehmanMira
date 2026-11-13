from functools import lru_cache
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration settings.

    Reads from system environment variables and a local .env file.
    System variables take precedence over the .env file.
    """
    
    # Required field: Gemini API Key
    google_api_key: str = Field(min_length=1)
    
    # Optional fields with predefined default values
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_fallback_models: list[str] = [
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-3.6-flash",
        "gemini-3.1-flash-lite",
        "gemini-3-flash-preview"
    ]
    db_path: Path = Path("data/availability_db/src/availability.db")
    properties_path: Path = Path("data/properties/src/properties.json")
    session_dir: Path = Path("sessions/")
    session_lock_timeout: int = 5
    max_user_input_length: int = 500
    debug: bool = False

    @field_validator("gemini_fallback_models", mode="before")
    @classmethod
    def _parse_fallback_models(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [m.strip() for m in v.split(",") if m.strip()]
        return v

    # Configuration for pydantic v2 settings resolution
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # Silently ignores any extra host OS environment variables
        frozen=True      # Enforces strict immutability after instantiation
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Retrieves the application settings singleton.

    Returns:
        Settings: An immutable configuration object containing application settings.
    """
    return Settings()
