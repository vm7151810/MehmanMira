import os
import json
from typing import Any
from functools import lru_cache
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Pre-populate os.environ from streamlit secrets if present (for Streamlit Community Cloud)
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, (str, int, float, bool)):
                val_str = str(v)
                os.environ[k] = val_str
                os.environ[k.upper()] = val_str
                os.environ[k.lower()] = val_str
except Exception:
    pass

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
    gemini_fallback_models: Any = [
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

    @field_validator("gemini_fallback_models", mode="after")
    @classmethod
    def _parse_fallback_models(cls, v):
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    pass
            return [m.strip() for m in v_str.split(",") if m.strip()]
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
