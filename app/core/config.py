import os
from pathlib import Path
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bitbucket_workspace: str = Field(default="")
    bitbucket_username: str = Field(default="")
    bitbucket_api_token: SecretStr = Field(default=SecretStr(""))
    
    # General app configurations
    bitbucket_work_dir: str = Field(default=str(Path.home() / "bitbucket-workspace"))
    bitbucket_api_base_url: str = Field(default="https://api.bitbucket.org/2.0")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Singleton initialization
settings = Settings()

def update_env_file(env_vars: dict[str, str]) -> None:
    """Updates the local .env file with new variables."""
    env_path = Path(".env")
    existing = {}
    
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k] = v
                    
    # Update state
    existing.update(env_vars)
    
    # Save back
    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")
